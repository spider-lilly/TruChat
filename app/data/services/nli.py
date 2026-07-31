import logging
import json
from django.conf import settings
from google import genai
from pydantic import BaseModel, Field
from .g import get_genai_client
from .schemas import (
    ClaimNormalization,
    Evidence,
    NLIResult
)

logger = logging.getLogger(__name__)
class NLIResponse(BaseModel):
    label: str = Field(description="Must be one of SUPPORTS, REFUTES, NEI")
    confidence: float = Field(description="A confidence score between 0.0 and 1.0")


def _truncate_evidence(text: str) -> str:
    """Keep NLI requests within the configured input budget."""
    limit = settings.NLI_MAX_INPUT_CHARS
    if len(text) <= limit:
        return text
    return text[: limit - 3].rsplit(" ", 1)[0] + "..."


def run_nli(
    claim: ClaimNormalization,
    evidence: Evidence,
) -> NLIResult:
    """
    Run Natural Language Inference between a claim
    and one evidence passage using Gemini API.
    """

    evidence_text = (
        evidence.cleaned or evidence.text or evidence.raw_text or evidence.title or ""
    ).strip()
    evidence_text = _truncate_evidence(evidence_text)
    claim_text = (
        claim.normalized or claim.cleaned or claim.original or ""
    ).strip()

    if not evidence_text or not claim_text:
        return NLIResult(
            evidence=evidence,
            label="NEI",
            confidence=0.0,
        )

    client = get_genai_client()
    
    prompt = f"""
Determine whether the following evidence supports, refutes, or has not enough information (NEI) regarding the claim.

Claim: {claim_text}
Evidence: {evidence_text}

Output a strict JSON object with 'label' (one of SUPPORTS, REFUTES, NEI) and 'confidence' (float between 0.0 and 1.0).
"""
    try:
        response = client.models.generate_content(
            model=getattr(settings, "LLM_MODEL", "gemini-1.5-flash"),
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=NLIResponse,
                temperature=0.0,
                max_output_tokens=settings.NLI_MAX_OUTPUT_TOKENS,
            ),
        )
        
        data = json.loads(response.text)
        label = str(data.get("label", "NEI")).upper()
        if label not in ("SUPPORTS", "REFUTES", "NEI"):
            label = "NEI"
            
        confidence = float(data.get("confidence", 0.0))
        
        return NLIResult(
            evidence=evidence,
            label=label,
            confidence=confidence,
        )
    except Exception:
        return NLIResult(
            evidence=evidence,
            label="NEI",
            confidence=0.0,
        )


def run_nli_batch(
    claim: ClaimNormalization,
    evidences: list[Evidence],
) -> list[NLIResult]:
    """
    Run NLI on multiple evidence passages in a single Gemini request.

    Raises exceptions on failure so the caller can fall back
    to individual run_nli() calls.
    """

    if not evidences:
        return []

    claim_text = (
        claim.normalized
        or claim.cleaned
        or claim.original
        or ""
    ).strip()

    if not claim_text:
        return [
            NLIResult(
                evidence=ev,
                label="NEI",
                confidence=0.0,
            )
            for ev in evidences
        ]

    prompt = f"""
Determine whether EACH evidence independently SUPPORTS, REFUTES,
or has NOT ENOUGH INFORMATION (NEI) regarding the claim.

Claim:
{claim_text}

Return ONLY a valid JSON array.

Example:

[
  {{
    "id": 0,
    "label": "SUPPORTS",
    "confidence": 0.92
  }},
  {{
    "id": 1,
    "label": "REFUTES",
    "confidence": 0.81
  }}
]

Rules:
- Every evidence ID MUST appear exactly once.
- id is the evidence number below.
- label MUST be SUPPORTS, REFUTES, or NEI.
- confidence MUST be between 0.0 and 1.0.
- Do NOT include markdown.
- Do NOT include explanations.
"""

    for i, ev in enumerate(evidences):
        evidence_text = (
            ev.cleaned
            or ev.text
            or ev.raw_text
            or ev.title
            or ""
        ).strip()

        evidence_text = _truncate_evidence(evidence_text)

        prompt += f"""

ID: {i}

Evidence:
{evidence_text}
"""

    client = get_genai_client()

    response = client.models.generate_content(
        model=getattr(settings, "LLM_MODEL", "gemini-1.5-flash"),
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.0,
            max_output_tokens=settings.NLI_MAX_OUTPUT_TOKENS,
        ),
    )

    try:
        logger.error("Batch NLI raw response:\n%s", response.text)
        data = json.loads(response.text)
    except Exception as e:
        raise RuntimeError("Gemini returned invalid JSON.") from e

    if not isinstance(data, list):
        raise RuntimeError("Expected JSON array from Gemini.")

    results = []
    seen = set()

    for item in data:

        try:
            idx = int(item["id"])
        except (KeyError, TypeError, ValueError):
            continue

        if idx < 0 or idx >= len(evidences):
            continue

        if idx in seen:
            continue

        seen.add(idx)

        label = str(
            item.get("label", "NEI")
        ).upper()

        if label not in (
            "SUPPORTS",
            "REFUTES",
            "NEI",
        ):
            label = "NEI"

        try:
            confidence = float(
                item.get("confidence", 0.0)
            )
        except Exception:
            confidence = 0.0

        confidence = max(
            0.0,
            min(confidence, 1.0),
        )

        results.append(
            NLIResult(
                evidence=evidences[idx],
                label=label,
                confidence=confidence,
            )
        )

    # Fill in missing evidence with NEI
    for idx, ev in enumerate(evidences):
        if idx not in seen:
            results.append(
                NLIResult(
                    evidence=ev,
                    label="NEI",
                    confidence=0.0,
                )
            )

    # Preserve original order
    results.sort(
        key=lambda r: evidences.index(r.evidence)
    )
    
    return results