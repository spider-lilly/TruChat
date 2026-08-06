
from .g import get_genai_client
import re
from typing import Tuple
from enum import Enum
from django.conf import settings
from google import genai
from config.settings import LLM_MODEL


class ClaimType(Enum):
    CLAIM = "claim"  # Verifiable factual statement about the world
    QUESTION = "question"  # Personal/opinion question or open-ended info request
    REQUEST = "request"  # Creative/task-generation request (joke, code, poem, summary, translation, etc.)
    UNCLEAR = "unclear"  # Ambiguous, needs LLM


# The rule/LLM layers classify *what kind of thing* the text is. This set
# answers the separate, real question the pipeline actually cares about:
# "should this enter fact-checking?" A type can be a clean, confident
# classification and still not belong in the pipeline - CLAIM is the only
# type that does.
NON_PIPELINE_TYPES = {
    ClaimType.QUESTION,
    ClaimType.REQUEST,
}

def _strip_chatter(text: str) -> str:
    """
    Remove conversational greetings/polite phrases from the beginning
    and end of a message without affecting the actual content.
    """

    text = text.strip()

    # Greetings at the beginning
    text = re.sub(
        r"^\s*(hi|hello|hey|yo|sup|good morning|good afternoon|good evening)\b[\s,!:.-]*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Polite endings
    text = re.sub(
        r"[\s,!:.-]*(thanks|thank you|thx)\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    )

    return text.strip()
def _detect_request(text: str):
    text = text.strip().lower()

    patterns = [

        # Creative
        r"^\s*tell me (a|an) (joke|story|riddle)\b",
        r"^\s*write (a|an) (story|essay|poem|script|song)\b",
        r"^\s*write (python|java|c\+\+|c#|javascript|sql)\b",
        r"^\s*generate (python|java|sql|code)\b",
        r"^\s*debug\b",
        r"^\s*fix (this )?code\b",
        r"^\s*translate\b",
        r"^\s*summarize\b",
        r"^\s*rewrite\b",
        r"^\s*paraphrase\b",
        r"^\s*proofread\b",
        r"^\s*edit this\b",# Image generation
        r"^\s*generate (an?|some)?\s*image\b",
        r"^\s*create (an?|some)?\s*image\b",
        r"^\s*make (an?|some)?\s*image\b",
        # Logos
        r"^\s*create (a|an)?\s*logo\b",
        r"^\s*design (a|an)?\s*logo\b",
        # Programming
        r"^\s*generate (python|java|c\+\+|c#|javascript|sql|code)\b",
        # Creative writing
        r"^\s*write (a|an) (story|essay|poem|script|song|speech)\b",
        r"^\s*give me (a|an) recipe\b",
        r"^\s*recipe for\b",
        r"^\s*draft (an?|the)? email\b",
        r"^\s*write (an?|the)? email\b",
    ]
    math_patterns = [
        r"^\s*\d+\s*[-+*/]\s*\d+",
        r"^\s*sqrt\s*\(",
        r"^\s*sin\s*\(",
        r"^\s*cos\s*\(",
        r"^\s*log\s*\(",
        r"^\s*integrate\b",
        r"^\s*differentiate\b",
        r"^\s*calculate\b",
        r"^\s*solve\b",
        r"^\s*convert\b",
    ]
    code_patterns = [
        r"#include",
        r"\bdef\s+\w+\(",
        r"public\s+static\s+void",
        r"console\.log\s*\(",
        r"function\s+\w*\(",
        r"SELECT\s+.+FROM",
        r"INSERT\s+INTO",
        r"UPDATE\s+\w+\s+SET",
        r"<html\b",
        
    ]

    for pattern in patterns:
        if re.search(pattern, text):
            return (ClaimType.REQUEST, 0.95)
    for pattern in math_patterns:
        if re.search(pattern, text):
            return (ClaimType.REQUEST, 0.90)
    for pattern in code_patterns:
        if re.search(pattern, text):
            return (ClaimType.REQUEST, 0.90)
    return None

def _detect_question(text: str):
    text = text.strip().lower()

    personal = [
        r"\b(do|does|did|are|is|can|could|will|would|should)\s+(you|u|i|we)\b",
        r"\bwhat do you think\b",
        r"\bin your opinion\b",
        r"\bhow are you\b",
    ]

    open_questions = [
        r"^\s*how (do|can|to)\b",
        r"^\s*why (do|does|did)\b",
        r"^\s*explain\b",
    ]

    for pattern in personal:
        if re.search(pattern, text):
            return (ClaimType.QUESTION, 0.90)

    for pattern in open_questions:
        if re.search(pattern, text):
            return (ClaimType.QUESTION, 0.85)

    return None

def _rule_based_detection(text: str):

    text = _strip_chatter(text)

    if not text:
        return (ClaimType.QUESTION, 0.99)

    detectors = (
        _detect_request,
        _detect_claim,
        _detect_question,
    )

    for detector in detectors:
        result = detector(text)
        if result is not None:
            return result

    return (ClaimType.UNCLEAR, 0.50)

def _detect_claim(text: str):
    text = text.lower()

    indicators = [
        r"\b(is|are|was|were)\s+(the|a|an)\b",
        r"\bcauses?\b",
        r"\bleads? to\b",
        r"\bresults? in\b",
        r"\bincreases?\b",
        r"\bdecreases?\b",
        r"\baffects?\b",
        r"\bcontains?\b",
        r"\bproves?\b",
        r"\bshows?\b",
        r"\baccording to\b",
        r"\bevidence\b",
        r"\bstudy\b",
        r"\bresearch\b",
        r"\b\d+\s*(%|percent|million|billion|thousand)\b",
    ]

    matches = sum(
        bool(re.search(pattern, text))
        for pattern in indicators
    )

    if matches >= 2:
        return (ClaimType.CLAIM, 0.90)

    if matches == 1:
        return (ClaimType.CLAIM, 0.65)

    return None

def _llm_based_detection(text: str) -> Tuple[ClaimType, float]:
    """
    Use LLM for ambiguous cases.
    Much faster than full NLI pipeline.
    """
    client = get_genai_client()
    
    prompt = f"""You are a claim detector for a misinformation-checking pipeline. \
Decide which of these three categories the text belongs to:

- CLAIM: a verifiable factual assertion about the world, worth fact-checking. \
This includes yes/no questions that are really asking to verify a checkable \
fact ("Is the earth round?", "Does coffee cause cancer?") - treat those as if \
rephrased into a statement.
- QUESTION: small talk, an opinion, or a personal question about the user/assistant \
(e.g. "do you smoke?"), or an open-ended request for an explanation rather than \
verification of a stated fact.
- REQUEST: an imperative/creative/task request asking the assistant to produce \
something (a joke, a poem, a piece of code, a recipe, a story,translation,summarization,rewriting \
,math,unit conversion,image generation,email drafting etc.) rather than \
assert or ask about a fact.

Text: "{text}"

Respond with ONLY:
1. TYPE: (CLAIM or QUESTION or REQUEST)
2. CONFIDENCE: (0.0-1.0)
3. REASON: (one sentence)

Examples:
- "Water boils at 100°C" → CLAIM, 0.98
- "Is Paris in France?" → CLAIM, 0.90 (verifiable fact, just phrased as a question)
- "Is the earth round?" → CLAIM, 0.95 (verifiable fact, just phrased as a question)
- "Do you smoke?" → QUESTION, 0.85 (personal question, not a public fact)
- "I think chocolate tastes good" → QUESTION, 0.80 (opinion, not fact)
- "What's up" → QUESTION, 0.95 (chatter)
- "Does coffee improve focus?" → CLAIM, 0.70 (checkable causal claim, phrased as a question)
- "Coffee increases alertness in most people" → CLAIM, 0.85
- "Tell me a joke about cats" → REQUEST, 0.95 (asking for creative output)
- "Write a Python function to sort a list" → REQUEST, 0.95 (asking for code)
- "Give me a recipe for banana bread" → REQUEST, 0.90 (asking for content, not verifying a fact)
"""
    
    try:
        response = client.models.generate_content(
            model=LLM_MODEL,  # Use fastest model for this
            contents=prompt,
        )
        
        text_response = response.text.lower()

        # Parse the TYPE: line specifically rather than doing a loose
        # substring search - avoids false positives from words that show
        # up in the REASON text (e.g. "not a claim" while type is REQUEST).
        type_match = re.search(r"type[:\s]+\**(claim|question|request)", text_response)
        if type_match:
            label = type_match.group(1)
            claim_type = {
                "claim": ClaimType.CLAIM,
                "question": ClaimType.QUESTION,
                "request": ClaimType.REQUEST,
            }[label]
        else:
            claim_type = ClaimType.UNCLEAR
        
        # Extract confidence
        confidence = 0.5
        import re as regex
        match = regex.search(r"confidence[:\s]+(\d+\.?\d*)", text_response)
        if match:
            confidence = float(match.group(1))
        
        return (claim_type, confidence)
    
    except Exception as e:
        # Fallback to unclear if LLM fails
        print(f"LLM detection failed: {e}")
        return (ClaimType.UNCLEAR, 0.5)


def is_claim(text: str, use_llm_threshold: float = 0.60) -> Tuple[bool, dict]:

    # Step 1: Rule-based detection (fast)
    rule_type, rule_confidence = _rule_based_detection(text)
    
    # If we're confident from rules, return immediately
    if rule_confidence > 0.85:
        return (
            rule_type == ClaimType.CLAIM,
            {
                "type": rule_type,
                "confidence": rule_confidence,
                "detection_method": "rule_based",
            }
        )
    
    # Step 2: LLM detection for unclear cases (slower but accurate)
    if rule_confidence <= use_llm_threshold:
        llm_type, llm_confidence = _llm_based_detection(text)
        return (
            llm_type == ClaimType.CLAIM,
            {
                "type": llm_type,
                "confidence": llm_confidence,
                "detection_method": "llm",
            }
        )
    
    # Return rule-based result if confidence is medium
    return (
        rule_type == ClaimType.CLAIM,
        {
            "type": rule_type,
            "confidence": rule_confidence,
            "detection_method": "rule_based",
        }
    )


