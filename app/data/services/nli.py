import os
import json
from django.conf import settings
from google import genai
from pydantic import BaseModel, Field

from .schemas import (
    ClaimNormalization,
    Evidence,
    NLIResult
)


class NLIResponse(BaseModel):
    label: str = Field(description="Must be one of SUPPORTS, REFUTES, NEI")
    confidence: float = Field(description="A confidence score between 0.0 and 1.0")


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
    claim_text = (
        claim.normalized or claim.cleaned or claim.original or ""
    ).strip()

    if not evidence_text or not claim_text:
        return NLIResult(
            evidence=evidence,
            label="NEI",
            confidence=0.0,
        )

    api_key = os.getenv("GEMINI_API_KEY", "")
    client = genai.Client(api_key=api_key)
    
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

