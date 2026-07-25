import os

os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("USE_TORCH", "1")

from transformers import pipeline
from .schemas import (
    ClaimNormalization,
    Evidence,
    NLIResult
)

nli_pipeline = pipeline(
    "text-classification",
    model="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli",
)

LABEL_MAP = {
    "ENTAILMENT": "SUPPORTS",
    "CONTRADICTION": "REFUTES",
    "NEUTRAL": "NEI",
}

def run_nli(
    claim: ClaimNormalization,
    evidence: Evidence,
) -> NLIResult:
    """
    Run Natural Language Inference between a claim
    and one evidence passage.
    """

    evidence_text = (
        evidence.cleaned or evidence.text or evidence.raw_text or evidence.title or ""
    ).strip()
    claim_text = (
        claim.normalized or claim.cleaned or claim.original or ""
    ).strip()

    if not evidence_text or not claim_text:
        return NLIResult(
            evidence=evidence,
            label="NEI",
            confidence=0.0,
        )

    raw = nli_pipeline(
        {
            "text": evidence_text,
            "text_pair": claim_text,
        },
        truncation=True,
        max_length=512,
    )

    if isinstance(raw, list) and len(raw) > 0:
        result = raw[0]
    elif isinstance(raw, dict):
        result = raw
    else:
        result = {"label": "NEUTRAL", "score": 0.0}

    label = str(result.get("label", "NEUTRAL")).upper()

    return NLIResult(
        evidence=evidence,
        label=LABEL_MAP.get(label, label),
        confidence=float(result.get("score", 0.0)),
    )
