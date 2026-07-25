import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import numpy as np
import redis
from django.conf import settings
from redis.commands.search.field import NumericField, TagField, TextField, VectorField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from redis.exceptions import ResponseError

from .schemas import ClaimNormalization, ScoreResult

if TYPE_CHECKING:
    from ..models import Claim

logger = logging.getLogger(__name__)

INDEX_NAME = "idx:claim_cache"
KEY_PREFIX = "claim:"


def get_redis_client():
    """Create and verify a Redis Stack client from Django settings."""
    try:
        client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD or None,
            decode_responses=False,
        )
        client.ping()
        return client
    except Exception as e:
        raise RuntimeError("Unable to connect to Redis cache.") from e


def create_vector_index():
    """Create the RediSearch HNSW index used for semantic cache lookups."""
    try:
        client = get_redis_client()

        try:
            client.ft(INDEX_NAME).info()
            return
        except ResponseError as e:
            if "unknown index name" not in str(e).lower():
                raise

        client.ft(INDEX_NAME).create_index(
            (
                TagField("id"),
                VectorField(
                    "embedding",
                    "HNSW",
                    {
                        "TYPE": "FLOAT32",
                        "DIM": settings.EMBEDDING_DIMENSION,
                        "DISTANCE_METRIC": "COSINE",
                    },
                ),
                TextField("normalized_claim"),
                TextField("verdict"),
                NumericField("confidence_score"),
                NumericField("credibility_score"),
                TextField("explanation"),
                NumericField("created_at"),
            ),
            definition=IndexDefinition(
                prefix=[KEY_PREFIX],
                index_type=IndexType.HASH,
            ),
        )
    except Exception as e:
        raise RuntimeError("Unable to create Redis vector cache index.") from e


def check_cache(
    normalized_claim: ClaimNormalization,
    embedding: np.ndarray,
):
    """Return a semantically similar cached score, or ``None`` on a cache miss."""
    try:
        create_vector_index()
        client = get_redis_client()
        vector = np.asarray(embedding, dtype=np.float32).tobytes()
        query = (
            Query("*=>[KNN 1 @embedding $embedding AS vector_distance]")
            .return_fields(
                "id",
                "verdict",
                "confidence_score",
                "credibility_score",
                "explanation",
                "vector_distance",
            )
            .sort_by("vector_distance")
            .paging(0, 1)
            .dialect(2)
        )
        result = client.ft(INDEX_NAME).search(query, {"embedding": vector})

        if not result.docs:
            return None

        cached = result.docs[0]
        similarity = 1.0 - float(cached.vector_distance)
        if similarity <= settings.CACHE_SIMILARITY_THRESHOLD:
            return None

        return ScoreResult(
            verdict=cached.verdict,
            confidence_score=float(cached.confidence_score),
            credibility_score=float(cached.credibility_score),
            explanation=cached.explanation,
        )
    except Exception as e:
        logger.warning("Redis cache unavailable or search failed: %s", e)
        return None


def store_cache(
    claim: "Claim",
    normalized: ClaimNormalization,
    embedding: np.ndarray,
    verdict: str,
    score: ScoreResult,
):
    """Store a completed claim evaluation as a Redis hash vector document."""
    try:
        create_vector_index()
        client = get_redis_client()
        claim_id = str(claim.id)
        key = f"{KEY_PREFIX}{claim_id}"
        client.hset(
            key,
            mapping={
                "id": claim_id,
                "embedding": np.asarray(embedding, dtype=np.float32).tobytes(),
                "normalized_claim": normalized.normalized,
                "verdict": verdict,
                "confidence_score": score.confidence_score,
                "credibility_score": score.credibility_score,
                "explanation": score.explanation,
                "created_at": datetime.now(timezone.utc).timestamp(),
            },
        )
    except Exception as e:
        logger.warning("Failed to store result in Redis cache: %s", e)


def delete_cache(claim_id):
    """Delete the cache document associated with one claim UUID."""
    try:
        client = get_redis_client()
        client.delete(f"{KEY_PREFIX}{claim_id}")
    except Exception as e:
        logger.warning("Failed to delete cache entry for claim %s: %s", claim_id, e)


def clear_cache():
    """Delete every claim-cache hash while preserving the vector index."""
    try:
        client = get_redis_client()
        keys = list(client.scan_iter(match=f"{KEY_PREFIX}*"))
        if keys:
            client.delete(*keys)
    except Exception as e:
        logger.warning("Failed to clear Redis cache: %s", e)
