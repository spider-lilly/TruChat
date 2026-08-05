
import numpy as np
from django.conf import settings
from google import genai
from .schemas import ClaimNormalization, Evidence
from typing import List


def _get_client() -> genai.Client:
    api_key = settings.GEMINI_API_KEY
    return genai.Client(api_key=api_key)


def embed_claim(claim: ClaimNormalization) -> np.ndarray:
    """Return a normalized float32 embedding for a normalized claim."""
    client = _get_client()
    text = claim.normalized or claim.cleaned or claim.original or ""
    if not text:
        return np.zeros(settings.EMBEDDING_DIMENSION, dtype=np.float32)

    response = client.models.embed_content(
        model=settings.EMBEDDING_MODEL,
        contents=text,
    )
    # The response has a list of embeddings; we take the first one
    return np.asarray(response.embeddings[0].values, dtype=np.float32)


def embed_evidence(evidence: Evidence) -> np.ndarray:
    """Return a normalized float32 embedding for cleaned evidence text."""
    client = _get_client()
    text = evidence.cleaned or evidence.text or evidence.raw_text or evidence.title or ""
    if not text:
        return np.zeros(settings.EMBEDDING_DIMENSION, dtype=np.float32)

    response = client.models.embed_content(
        model=settings.EMBEDDING_MODEL,
        contents=text,
    )
    return np.asarray(response.embeddings[0].values, dtype=np.float32)

def embed_evidence_batch(evidences: list[Evidence]) -> list[np.ndarray]:
    """
    Return normalized float32 embeddings for multiple evidence objects.
    Falls back to zero vectors if an item has no text.
    """
    client = _get_client()

    texts = []
    valid_indices = []

    embeddings = [
        np.zeros(settings.EMBEDDING_DIMENSION, dtype=np.float32)
        for _ in evidences
    ]

    for i, evidence in enumerate(evidences):
        text = (
            evidence.cleaned
            or evidence.text
            or evidence.raw_text
            or evidence.title
            or ""
        )

        if text:
            texts.append(text)
            valid_indices.append(i)

    if not texts:
        return embeddings

    response = client.models.embed_content(
        model=settings.EMBEDDING_MODEL,
        contents=texts,
    )

    for idx, embedding in zip(valid_indices, response.embeddings):
        embeddings[idx] = np.asarray(
            embedding.values,
            dtype=np.float32,
        )

    return embeddings


def rerank_evidence(
    claim_embedding: np.ndarray,
    evidences: list[Evidence],
    evidence_embeddings: list[np.ndarray],
    top_k: int = settings.TOP_EVIDENCE_FOR_NLI,
) -> list[dict]:
 
    
    ranked = []

    claim_norm = np.linalg.norm(claim_embedding)

    if claim_norm == 0:
        return []

    for evidence, embedding in zip(
        evidences,
        evidence_embeddings,
    ):

        emb_norm = np.linalg.norm(embedding)

        if emb_norm == 0:
            continue

        similarity = np.dot(
            claim_embedding,
            embedding,
        ) / (claim_norm * emb_norm)

        ranked.append(
            {
                "similarity": similarity,
                "evidence": evidence,
                "embedding": embedding,
            }
        )

    ranked.sort(
        key=lambda x: x["similarity"],
        reverse=True,
    )

    return ranked[:top_k]