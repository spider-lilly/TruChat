import json
import logging
import os
from collections import defaultdict
from django.conf import settings
from openai import OpenAI

from .schemas import (
    ClaimNormalization,
    Evidence,
    NLIResult,
    ScoreResult,
)

logger = logging.getLogger(__name__)


def get_openai_client() -> tuple[OpenAI, str]:
    """Return an OpenAI-compatible client instance and model name lazily."""
    api_key = (
        getattr(settings, "API_KEY", None)
        or os.getenv("LLM_KEY")
        or os.getenv("API_KEY")
        or os.getenv("GROQ_API_KEY")
        or os.getenv("XAI_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or "missing-key"
    )

    if api_key.startswith("gsk_"):
        base_url = "https://api.groq.com/openai/v1"
        model = getattr(settings, "LLM_MODEL", None)
        if not model or "grok" in model or "gpt" in model:
            model = "llama-3.3-70b-versatile"
    elif api_key.startswith("xai-"):
        base_url = "https://api.x.ai/v1"
        model = getattr(settings, "LLM_MODEL", None)
        if not model or model in ("grok-4", "grok-latest", "grok-2-latest"):
            model = "grok-2-1212"
    elif api_key.startswith("AIzaSy"):
        base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        model = getattr(settings, "LLM_MODEL", None)
        if not model or "grok" in model:
            model = "gemini-1.5-flash"
    elif api_key.startswith("sk-or-"):
        base_url = "https://openrouter.ai/api/v1"
        model = getattr(settings, "LLM_MODEL", None)
        if not model or "grok" in model:
            model = "meta-llama/llama-3.2-3b-instruct:free"
    else:
        base_url = "https://api.openai.com/v1"
        model = getattr(settings, "LLM_MODEL", None)
        if not model or "grok" in model:
            model = "gpt-4o-mini"

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )
    return client, model


def aggregate_verdict(
    nli_results: list[NLIResult],
) -> str:
    """
    Aggregate NLI results using signal-priority weighting.
    Gives precedence to high-confidence SUPPORTS/REFUTES evidence over background NEI items.
    """
    if not nli_results:
        return "NEI"

    supports = [r for r in nli_results if r.label == "SUPPORTS"]
    refutes = [r for r in nli_results if r.label == "REFUTES"]

    max_support = max((r.confidence for r in supports), default=0.0)
    max_refute = max((r.confidence for r in refutes), default=0.0)

    # 1. High-confidence direct signal check
    if max_support >= 0.50 and max_support >= max_refute:
        return "SUPPORTS"

    if max_refute >= 0.50 and max_refute > max_support:
        return "REFUTES"

    # 2. Weighted score accumulation (boost SUPPORTS & REFUTES 3x over NEI)
    scores = defaultdict(float)
    for r in nli_results:
        weight = 3.0 if r.label in ("SUPPORTS", "REFUTES") else 1.0
        scores[r.label] += r.confidence * weight

    return max(scores, key=scores.get)


def _build_prompt(
    claim: ClaimNormalization,
    verdict: str,
    evidence: list[Evidence],
    nli_results: list[NLIResult],
) -> str:
    """Build the prompt sent to the LLM, trimming evidence snippets to fit token limits."""
    prompt = []
    prompt.append(f"Claim:\n{claim.original}\n")
    prompt.append(f"Final Verdict:\n{verdict}\n")
    prompt.append("Evidence:\n")

    # Limit to top 6 evidence items and trim content to 500 characters to stay within token limits
    for i, (ev, nli) in enumerate(list(zip(evidence, nli_results))[:6], start=1):
        content = (ev.cleaned or ev.text or ev.raw_text or "").strip()
        if len(content) > 500:
            content = content[:500] + "..."

        prompt.append(
            f"""
Evidence {i}

Title:
{ev.title}

Source:
{ev.source}

URL:
{ev.url}

NLI Label:
{nli.label}

NLI Confidence:
{nli.confidence:.3f}

Content:
{content}
"""
        )

    prompt.append(
        """
Your task is NOT to determine whether the claim is true or false.
The verdict has already been computed.

Evaluate only:

1. confidence_score
   How confident are you in the provided verdict?
   Value between 0 and 1.

2. credibility_score
   How credible are the provided sources and evidence?
   Value between 0 and 1.

3. explanation
   Explain your reasoning in under 150 words.

Return ONLY valid JSON.

{
    "confidence_score": float,
    "credibility_score": float,
    "explanation": string
}
"""
    )

    return "\n".join(prompt)


def score_claim(
    claim: ClaimNormalization,
    evidence: list[Evidence],
    nli_results: list[NLIResult],
) -> ScoreResult:
    """
    Generate confidence and credibility scores using the LLM with robust fallback.
    """
    verdict = aggregate_verdict(nli_results)

    # Compute rule-based fallback metrics
    if nli_results:
        winning_scores = [n.confidence for n in nli_results if n.label == verdict]
        avg_confidence = sum(winning_scores) / len(winning_scores) if winning_scores else 0.5
        source_count = len(set(e.source for e in evidence))
        credibility = min(1.0, 0.4 + (source_count * 0.15) + (avg_confidence * 0.3))
    else:
        avg_confidence = 0.5
        credibility = 0.5

    fallback_explanation = (
        f"Based on evaluation of {len(evidence)} evidence source(s), the claim received a verdict of '{verdict}' "
        f"with an NLI confidence score of {avg_confidence:.2f}."
    )

    api_key = getattr(settings, "API_KEY", None) or os.getenv("API_KEY")
    if not api_key or api_key.startswith("replace-with") or api_key == "missing-key":
        logger.warning("API_KEY not configured. Using rule-based fallback scoring.")
        return ScoreResult(
            verdict=verdict,
            confidence_score=round(float(avg_confidence), 2),
            credibility_score=round(float(credibility), 2),
            explanation=fallback_explanation,
        )

    try:
        prompt = _build_prompt(
            claim,
            verdict,
            evidence,
            nli_results,
        )
        client, model = get_openai_client()
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert evidence evaluator.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            response_format={"type": "json_object"},
            timeout=15,
        )

        result = json.loads(response.choices[0].message.content)
        return ScoreResult(
            verdict=verdict,
            confidence_score=float(result.get("confidence_score", avg_confidence)),
            credibility_score=float(result.get("credibility_score", credibility)),
            explanation=str(result.get("explanation", fallback_explanation)),
        )
    except Exception as e:
        logger.warning("LLM scoring call failed: %s. Using rule-based fallback scoring.", e)
        return ScoreResult(
            verdict=verdict,
            confidence_score=round(float(avg_confidence), 2),
            credibility_score=round(float(credibility), 2),
            explanation=fallback_explanation,
        )