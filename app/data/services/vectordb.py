"""PostgreSQL/pgvector-backed exact and semantic claim result lookup."""

from typing import TYPE_CHECKING

import numpy as np
from django.conf import settings
from pgvector.django import CosineDistance

from ..models import ClaimEmbedding, ClaimStatus, ExactClaimCache
from .schemas import ScoreResult

if TYPE_CHECKING:
    from .schemas import ClaimNormalization


def get_exact_result(normalized_claim: "ClaimNormalization") -> ScoreResult | None:
    """Return a score without embedding or searching for an exact normalized claim."""
    cached = ExactClaimCache.objects.filter(
        normalized_claim=normalized_claim.normalized,
    ).first()
    if cached is None:
        return None

    return ScoreResult(
        verdict=cached.verdict,
        credibility_score=cached.credibility_score,
        explanation=cached.explanation,
    )


def get_similar_result(embedding: np.ndarray) -> ScoreResult | None:
    """Find a completed, sufficiently similar claim with pgvector cosine KNN."""
    vector = np.asarray(embedding, dtype=np.float32).tolist()
    nearest = (
        ClaimEmbedding.objects.select_related("claim__final_result")
        .filter(
            claim__status=ClaimStatus.COMPLETED,
            claim__final_result__isnull=False,
        )
        .annotate(distance=CosineDistance("embedding_vector", vector))
        .order_by("distance")
        .first()
    )
    if nearest is None or nearest.distance is None:
        return None

    similarity = 1.0 - float(nearest.distance)
    if similarity < settings.CACHE_SIMILARITY_THRESHOLD:
        return None

    result = nearest.claim.final_result
    return ScoreResult(
        verdict=result.verdict,
        credibility_score=result.credibility_score,
        explanation=result.llm_explanation,
    )


def store_exact_result(normalized_claim: "ClaimNormalization", score: ScoreResult) -> None:
    """Upsert the direct cache record after a claim evaluation succeeds."""
    ExactClaimCache.objects.update_or_create(
        normalized_claim=normalized_claim.normalized,
        defaults={
            "verdict": score.verdict,
            "credibility_score": score.credibility_score,
            "explanation": score.explanation,
        },
    )
