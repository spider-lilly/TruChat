from dataclasses import asdict
import logging

from django.db import transaction

from .cache import check_cache, store_cache
from .clean import clean_text
from .embedding import embed_claim, embed_evidence
from .nli import run_nli
from .normalize import normalize_claim, normalize_evidence
from .schemas import ScoreResult
from .scoring import aggregate_verdict, score_claim
from .search import search_claim
from ..models import (
    Claim,
    ClaimEmbedding,
    ClaimStatus,
    FinalResult,
    NLIResult,
    Source,
    SourceEmbedding,
)

logger = logging.getLogger(__name__)


def _pipeline_error(claim, stage, error):
    logger.exception(
        "Pipeline failed at %s",
        stage,
    )

    if claim is not None:
        claim.status = ClaimStatus.FAILED
        claim.save(update_fields=["status"])

    raise RuntimeError(
        f"Pipeline failed at stage: {stage}"
    ) from error


def process_claim(
    claim_text: str,
) -> ScoreResult:
    """Create Claim"""

    claim = None

    try:
        claim = Claim.objects.create(
            claim_text=claim_text,
            status=ClaimStatus.PROCESSING,
        )
    except Exception:
        logger.exception("Failed to create claim")
        raise

    """Clean Stage"""
    try:
        cleaned = clean_text(claim.claim_text)
    except Exception as e:
        _pipeline_error(
            claim,
            "clean_text",
            e,
        )

    """Normalize Stage"""
    try:
        normalized = normalize_claim(cleaned)
    except Exception as e:
        _pipeline_error(
            claim,
            "normalize_claim",
            e,
        )

    claim.cleaned_claim = normalized.cleaned
    claim.normalized_claim = normalized.normalized
    claim.canonical_claim = normalized.canonical
    claim.fingerprint = normalized.fingerprint
    claim.entities = asdict(normalized.entities)
    claim.keywords = normalized.keywords
    claim.numbers = normalized.numbers
    claim.dates = normalized.dates

    """Embed Claim"""
    try:
        claim_embedding = embed_claim(normalized)
    except Exception as e:
        _pipeline_error(
            claim,
            "embed_claim",
            e,
        )

    """Redis Lookup"""
    try:
        cached_result = check_cache(
            normalized,
            claim_embedding,
        )
    except Exception as e:
        logger.warning("Redis cache check failed, proceeding with full pipeline: %s", e)
        cached_result = None

    if cached_result is not None:
        try:
            claim.status = ClaimStatus.COMPLETED
            claim.save(update_fields=["status"])
        except Exception as e:
            _pipeline_error(
                claim,
                "update_cached_claim_status",
                e,
            )

        return cached_result

    """Search Evidence"""
    try:
        evidence = search_claim(normalized)
    except Exception as e:
        _pipeline_error(claim, "search_claim", e)

    """Normalize Evidence"""
    normalized_evidence = []
    for ev in evidence:
        try:
            normalized_evidence.append(normalize_evidence(ev))
        except Exception:
            logger.exception("Failed to normalize evidence: %s", ev.url)
            continue

    """Embed Evidence"""
    embedded_evidence = []
    for ev in normalized_evidence:
        try:
            embedding = embed_evidence(ev)
            embedded_evidence.append(
                {
                    "evidence": ev,
                    "embedding": embedding,
                }
            )
        except Exception as e:
            logger.exception("Embedding failed for %s: %s", ev.url, e)
            continue

    """Run NLI"""
    if not embedded_evidence:
        _pipeline_error(
            claim,
            "run_nli",
            RuntimeError("No usable evidence found."),
        )

    nli_results = []
    for item in embedded_evidence:
        try:
            result = run_nli(normalized, item["evidence"])
            item["nli"] = result
            nli_results.append(result)
        except Exception as e:
            logger.exception("NLI failed for %s: %s", item["evidence"].url, e)
            continue

    if not nli_results:
        _pipeline_error(
            claim,
            "run_nli",
            RuntimeError("No NLI results generated"),
        )

    """Aggregate Verdict"""
    try:
        verdict = aggregate_verdict(nli_results)
    except Exception as e:
        _pipeline_error(claim, "aggregate_verdict", e)

    """Score Claim"""
    try:
        evidence = [item["evidence"] for item in embedded_evidence]
        score = score_claim(normalized, evidence, nli_results)
    except Exception as e:
        _pipeline_error(claim, "score_claim", e)

    write_stage = "database_transaction"
    try:
        with transaction.atomic():
            """Save Normalized Claim"""
            try:
                claim.save(
                    update_fields=[
                        "cleaned_claim",
                        "normalized_claim",
                        "canonical_claim",
                        "fingerprint",
                        "entities",
                        "keywords",
                        "numbers",
                        "dates",
                    ]
                )
            except Exception:
                write_stage = "save_normalized_claim"
                raise

            """Save Claim Embedding"""
            try:
                ClaimEmbedding.objects.create(
                    claim=claim,
                    embedding_vector=claim_embedding.tolist(),
                )
            except Exception:
                write_stage = "save_claim_embedding"
                raise

            """Save Sources"""
            for item in embedded_evidence:
                ev = item["evidence"]
                try:
                    source = Source.objects.create(
                        claim=claim,
                        url=ev.url,
                        title=ev.title,
                        source_name=ev.source,
                        raw_text=ev.text,
                        cleaned_text=ev.cleaned,
                    )
                except Exception:
                    write_stage = "save_source"
                    raise

                item["source"] = source

            """Save Source Embeddings"""
            for item in embedded_evidence:
                try:
                    SourceEmbedding.objects.create(
                        source=item["source"],
                        embedding_vector=item["embedding"].tolist(),
                    )
                except Exception:
                    write_stage = "save_source_embedding"
                    raise

            """Save NLI Results"""
            for item in embedded_evidence:
                if "nli" not in item:
                    continue

                result = item["nli"]
                supports = 0.0
                contradicts = 0.0
                neutral = 0.0

                if result.label == "SUPPORTS":
                    supports = result.confidence
                elif result.label == "REFUTES":
                    contradicts = result.confidence
                else:
                    neutral = result.confidence

                try:
                    NLIResult.objects.create(
                        source=item["source"],
                        supports=supports,
                        contradicts=contradicts,
                        neutral=neutral,
                        label=result.label,
                    )
                except Exception:
                    write_stage = "save_nli_result"
                    raise

            """Save Final Result"""
            try:
                FinalResult.objects.create(
                    claim=claim,
                    verdict=verdict,
                    confidence_score=score.confidence_score,
                    credibility_score=score.credibility_score,
                    llm_explanation=score.explanation,
                )
            except Exception:
                write_stage = "save_final_result"
                raise

            """Update Status"""
            try:
                claim.status = ClaimStatus.COMPLETED
                claim.save(update_fields=["status"])
            except Exception:
                write_stage = "update_claim_status"
                raise
    except Exception as e:
        _pipeline_error(claim, write_stage, e)

    try:
        store_cache(
            claim,
            normalized,
            claim_embedding,
            verdict,
            score,
        )
    except Exception:
        logger.exception("Failed to store result in Redis cache.")

    return score
