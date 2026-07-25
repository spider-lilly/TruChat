import os

os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("USE_TORCH", "1")

import numpy as np
from django.conf import settings
from sentence_transformers import SentenceTransformer

from .schemas import ClaimNormalization, Evidence


model = SentenceTransformer(settings.EMBEDDING_MODEL)


def embed_claim(claim: ClaimNormalization) -> np.ndarray:
    """Return a normalized float32 embedding for a normalized claim."""
    return np.asarray(
        model.encode(claim.normalized, normalize_embeddings=True),
        dtype=np.float32,
    )


def embed_evidence(evidence: Evidence) -> np.ndarray:
    """Return a normalized float32 embedding for cleaned evidence text."""
    return np.asarray(
        model.encode(evidence.cleaned, normalize_embeddings=True),
        dtype=np.float32,
    )
