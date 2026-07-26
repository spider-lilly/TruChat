import os
import re
import json
from typing import Any
from django.conf import settings
from google import genai
from .g import get_genai_client
from pydantic import BaseModel

import dateparser

from .schemas import (
    ClaimNormalization,
    Entities,
    Evidence,
    SearchQueries,
)
from .clean import clean_text


class EntitiesModel(BaseModel):
    persons: list[str] = []
    organizations: list[str] = []
    locations: list[str] = []
    events: list[str] = []
    products: list[str] = []


class NormalizeResponse(BaseModel):
    canonical: str = ""
    fingerprint: str = ""
    keywords: list[str] = []
    numbers: list[str] = []
    dates: list[str] = []
    entities: EntitiesModel
    action: str = ""





def normalize_claim(cleaned: dict[str, Any]) -> ClaimNormalization:
    """
    Normalize a cleaned claim.
    """
    text = cleaned["cleaned_text"]
    
    prompt = f"""
Analyze the following text and extract the required fields.
Text: "{text}"

1. 'canonical': A space-separated string of lemmatized tokens (excluding punctuation/spaces).
2. 'fingerprint': A space-separated string of unique, lowercased lemmatized tokens (excluding stop words/punctuation).
3. 'keywords': Up to 10 key phrases (max 2 words each).
4. 'numbers': A list of all numbers found in the text.
5. 'dates': A list of dates mentioned.
6. 'entities': Grouped by persons, organizations, locations, events, and products.
7. 'action': The root verb of the main sentence.
"""
    try:
        client = get_genai_client()
        response = client.models.generate_content(
            model=getattr(settings, "LLM_MODEL", "gemini-1.5-flash"),
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=NormalizeResponse,
                temperature=0.0,
                max_output_tokens=settings.NORMALIZATION_MAX_OUTPUT_TOKENS,
            ),
        )
        data = json.loads(response.text)
        
        canonical = data.get("canonical", "")
        fingerprint = data.get("fingerprint", "")
        keywords = data.get("keywords", [])
        numbers = data.get("numbers", [])
        dates_raw = data.get("dates", [])
        
        entities_data = data.get("entities", {})
        entities = Entities(
            persons=entities_data.get("persons", []),
            organizations=entities_data.get("organizations", []),
            locations=entities_data.get("locations", []),
            events=entities_data.get("events", []),
            products=entities_data.get("products", []),
        )
        action = data.get("action", "")
    except Exception:
        canonical = text
        fingerprint = text
        keywords = []
        numbers = []
        dates_raw = []
        entities = Entities()
        action = ""

    dates = []
    for d in dates_raw:
        parsed = dateparser.parse(d)
        if parsed:
            dates.append(parsed.date().isoformat())
        else:
            dates.append(d)

    entity_list = (
        entities.persons
        + entities.organizations
        + entities.locations
        + entities.events
        + entities.products
    )
    entity_string = " ".join(entity_list)
    gdelt = " ".join(filter(None, [entity_string, action, *dates]))

    search_queries = SearchQueries(
        general=text,
        tavily=text,
        wikipedia=entity_string,
        wikidata=entity_string,
        gdelt=gdelt,
    )
    
    return ClaimNormalization(
        original=text,
        cleaned=text,
        normalized=text,
        canonical=canonical,
        fingerprint=fingerprint,
        entities=entities,
        keywords=keywords,
        numbers=numbers,
        dates=dates,
        search_queries=search_queries,
    )


def normalize_evidence(evidence: Evidence) -> Evidence:
    """
    Normalize an Evidence object.
    Unlike claims, evidence is minimally transformed
    to preserve factual wording for NLI.
    """
    cleaned = clean_text(evidence.text)
    text = cleaned["cleaned_text"]
    
    normalized_text = " ".join(text.split())
    normalized_text = re.sub(r"\s+([.,!?])", r"\1", normalized_text)
    evidence.cleaned = normalized_text
    
    return evidence
