from openai import OpenAI
import json
from collections import defaultdict
from django.conf import settings

from .schemas import (
    ClaimNormalization,
    Evidence,
    NLIResult,
    ScoreResult,
)

client = OpenAI(
    api_key=settings.API_KEY,
    base_url="https://api.x.ai/v1",
)

def aggregate_verdict(
    nli_results: list[NLIResult],
) -> str:
    """
    Aggregate NLI results using weighted confidence.
    """

    scores = defaultdict(float)

    for result in nli_results:
        scores[result.label] += result.confidence

    return max(scores, key=scores.get)

def _build_prompt(
    claim: ClaimNormalization,
    verdict: str,
    evidence: list[Evidence],
    nli_results: list[NLIResult],
) -> str:
    """
    Build the prompt sent to the LLM.
    """

    prompt = []

    prompt.append(f"Claim:\n{claim.original}\n")

    prompt.append(f"Final Verdict:\n{verdict}\n")

    prompt.append("Evidence:\n")

    for i, (ev, nli) in enumerate(zip(evidence, nli_results), start=1):

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
{ev.cleaned}
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
    Generate confidence and credibility scores using the LLM.
    """

    verdict = aggregate_verdict(nli_results)

    prompt = _build_prompt(
        claim,
        verdict,
        evidence,
        nli_results,
    )

    response = client.chat.completions.create(
        model=settings.LLM_MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert evidence evaluator."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        response_format={
            "type": "json_object"
        },
    )

    result = json.loads(
        response.choices[0].message.content
    )

    return ScoreResult(
        verdict=verdict,
        confidence_score=result["confidence_score"],
        credibility_score=result["credibility_score"],
        explanation=result["explanation"],
    )