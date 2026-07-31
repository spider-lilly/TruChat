
import numpy as np
from django.conf import settings
from google import genai
from .schemas import ClaimNormalization, Evidence



def _get_client() -> genai.Client:
    api_key = settings.GEMINI_API_KEY
    return genai.Client(api_key=api_key)


def embed_claim(claim: ClaimNormalization) -> np.ndarray:
    """Return a normalized float32 embedding for a normalized claim."""
    client = _get_client()
    text = claim.normalized or claim.cleaned or claim.original or ""
    if not text:
        return np.zeros(768, dtype=np.float32)

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
        return np.zeros(768, dtype=np.float32)

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
        np.zeros(768, dtype=np.float32)
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
