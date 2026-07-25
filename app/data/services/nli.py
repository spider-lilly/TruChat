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

    result = nli_pipeline(
        {
            "text": evidence.cleaned,
            "text_pair": claim.normalized,
        }
    )[0]

    label = result["label"].upper()

    return NLIResult(
        evidence=evidence,
        label=LABEL_MAP.get(label, label),
        confidence=result["score"],
    )
