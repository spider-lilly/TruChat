from dataclasses import asdict
import logging

from django.conf import settings
from django.db import transaction
from services.imgtotext import load_image, ocr_space_extract, clean_ocr_text
from services.clean import clean_text
from services.embedding import embed_claim, embed_evidence, embed_evidence_batch , rerank_evidence
from services.nli import run_nli,run_nli_batch
from services.normalize import normalize_claim, normalize_evidence
from services.schemas import ScoreResult
from services.scoring import aggregate_verdict, score_claim
from services.search import search_claim
from services.vectordb import get_exact_result, get_similar_result, store_exact_result
from .models import (
    Claim,
    ClaimEmbedding,
    ClaimStatus,
    FinalResult,
    NLIResult,
    Source,
    SourceEmbedding,
)

logger = logging.getLogger(__name__)


def _select_evidence(evidence):
    """Deduplicate results and retain a small, source-diverse evidence set."""
    unique = []
    seen_urls = set()
    for item in evidence:
        url = (item.url or "").strip().lower()
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        unique.append(item)

    # Take one result from each source before taking additional results. This
    # avoids a single search provider consuming the entire LLM budget.
    selected = []
    remaining = list(unique)
    while remaining and len(selected) < settings.MAX_EVIDENCE_PER_CLAIM:
        seen_sources = set()
        next_round = []
        for item in remaining:
            if item.source in seen_sources:
                next_round.append(item)
                continue
            selected.append(item)
            seen_sources.add(item.source)
            if len(selected) == settings.MAX_EVIDENCE_PER_CLAIM:
                break
        else:
            remaining = next_round
            continue
        break

    return selected


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


def process_image(
    image_input,
    user=None,
):

    # Load image
    image_bytes, mime_type = load_image(image_input)

    # OCR
    raw_text = ocr_space_extract(
        image_bytes=image_bytes,
        mime_type=mime_type,
    )

    # Local cleanup
    extracted_text = clean_ocr_text(raw_text)

    if not extracted_text.strip():
        raise ValueError(
            "No readable text was found in the uploaded image."
        )

    # Reuse the existing text pipeline
    return process_claim(
        claim_text=extracted_text,
        user=user,
        input_source="IMAGE",
    )

def process_claim(
    claim_text: str,
    user=None,
    input_source: str = "TEXT",
) -> ScoreResult:
    """Create Claim"""

    claim = None

    try:
        claim = Claim.objects.create(
            user=user,
            claim_text=claim_text,
            status=ClaimStatus.PROCESSING,
            input_source=input_source,
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

    """Exact PostgreSQL cache lookup"""
    try:
        cached_result = get_exact_result(normalized)
    except Exception as e:
        logger.warning("Exact cache lookup failed, proceeding with full pipeline: %s", e)
        cached_result = None

    if cached_result is not None:
        try:
            claim.cleaned_claim = normalized.cleaned
            claim.normalized_claim = normalized.normalized
            claim.canonical_claim = normalized.canonical
            claim.fingerprint = normalized.fingerprint
            claim.entities = asdict(normalized.entities)
            claim.keywords = normalized.keywords
            claim.numbers = normalized.numbers
            claim.dates = normalized.dates
            claim.status = ClaimStatus.COMPLETED
            claim.save()
            FinalResult.objects.create(
                claim=claim,
                verdict=cached_result.verdict,
                credibility_score=cached_result.credibility_score,
                llm_explanation=cached_result.explanation,
            )
        except Exception as e:
            _pipeline_error(
                claim,
                "update_cached_claim_status",
                e,
            )

        return cached_result

    """Embed Claim"""
    try:
        claim_embedding = embed_claim(normalized)
    except Exception as e:
        _pipeline_error(claim, "embed_claim", e)

    """pgvector semantic lookup"""
    try:
        cached_result = get_similar_result(claim_embedding)
    except Exception as e:
        logger.warning("pgvector cache lookup failed, proceeding with full pipeline: %s", e)
        cached_result = None

    if cached_result is not None:
        try:
            claim.cleaned_claim = normalized.cleaned
            claim.normalized_claim = normalized.normalized
            claim.canonical_claim = normalized.canonical
            claim.fingerprint = normalized.fingerprint
            claim.entities = asdict(normalized.entities)
            claim.keywords = normalized.keywords
            claim.numbers = normalized.numbers
            claim.dates = normalized.dates
            claim.status = ClaimStatus.COMPLETED
            claim.save()
            ClaimEmbedding.objects.create(claim=claim, embedding_vector=claim_embedding.tolist())
            FinalResult.objects.create(
                claim=claim,
                verdict=cached_result.verdict,
                credibility_score=cached_result.credibility_score,
                llm_explanation=cached_result.explanation,
            )
            store_exact_result(normalized, cached_result)
        except Exception as e:
            _pipeline_error(claim, "save_semantic_cache_hit", e)

        return cached_result

    """Search Evidence"""
    try:
        evidence = search_claim(normalized)
    except Exception as e:
        _pipeline_error(claim, "search_claim", e)

    evidence = _select_evidence(evidence)

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

    if normalized_evidence:
    
        try:
            embeddings = embed_evidence_batch(normalized_evidence)

            if len(embeddings) != len(normalized_evidence):
                raise ValueError(
                    f"Expected {len(normalized_evidence)} embeddings, "
                    f"received {len(embeddings)}."
                )

            embedded_evidence = [
                {
                    "evidence": ev,
                    "embedding": emb,
                }
                for ev, emb in zip(normalized_evidence, embeddings)
            ]

        except Exception as batch_error:
            logger.exception(
                "Batch embedding failed. Falling back to single embeddings. Error: %s",
                batch_error,
            )

            for ev in normalized_evidence:
                try:
                    embedding = embed_evidence(ev)

                    embedded_evidence.append(
                        {
                            "evidence": ev,
                            "embedding": embedding,
                        }
                    )

                except Exception as single_error:
                    logger.exception(
                        "Embedding failed for %s: %s",
                        ev.url,
                        single_error,
                    )

    """Rerank Evidence"""
    try:
        embedded_evidence = rerank_evidence(
            claim_embedding,
            [item["evidence"] for item in embedded_evidence],
            [item["embedding"] for item in embedded_evidence],
            top_k=settings.TOP_EVIDENCE_FOR_NLI,
        )
    except Exception as e:
        _pipeline_error(claim, "rerank_evidence", e)
    """Run NLI"""

    if not embedded_evidence:
        _pipeline_error(
            claim,
            "run_nli",
            RuntimeError("No usable evidence found."),
        )

    BATCH_SIZE = 3

    nli_results = []

    for start in range(
        0,
        len(embedded_evidence),
        BATCH_SIZE,
    ):

        batch = embedded_evidence[
            start:start + BATCH_SIZE
        ]

        try:

            results = run_nli_batch(
                normalized,
                [
                    item["evidence"]
                    for item in batch
                ],
            )

            if len(results) != len(batch):
                raise RuntimeError(
                    f"Expected {len(batch)} NLI results "
                    f"but received {len(results)}."
                )

            for item, result in zip(batch, results):

                item["nli"] = result

                nli_results.append(result)

        except Exception as batch_error:

            logger.exception(
                "Batch NLI failed. "
                "Falling back to individual NLI. Error: %s",
                batch_error,
            )

            for item in batch:

                try:

                    result = run_nli(
                        normalized,
                        item["evidence"],
                    )

                    item["nli"] = result

                    nli_results.append(result)

                except Exception as single_error:

                    logger.exception(
                        "NLI failed for %s: %s",
                        item["evidence"].url,
                        single_error,
                    )

                    continue

    if not nli_results:
        _pipeline_error(
            claim,
            "run_nli",
            RuntimeError("No NLI results generated."),
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
        store_exact_result(normalized, score)
    except Exception:
        logger.exception("Failed to store exact PostgreSQL cache result.")

    return score
