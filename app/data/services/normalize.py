import re
from typing import Any

import dateparser
import spacy
import yake

from .schemas import (
    ClaimNormalization,
    Entities,
    Evidence,
    SearchQueries,
)
from .clean import clean_text


nlp = spacy.load("en_core_web_lg")

keyword_extractor = yake.KeywordExtractor(
    lan="en",
    n=2,
    dedupLim=0.8,
    top=10,
)

def _extract_entities(doc) -> Entities:
    """
    Extract named entities from a spaCy Doc object.
    """

    entities = Entities()

    mapping = {
        "PERSON": entities.persons,
        "ORG": entities.organizations,
        "GPE": entities.locations,
        "LOC": entities.locations,
        "EVENT": entities.events,
        "PRODUCT": entities.products,
    }

    for ent in doc.ents:

        target = mapping.get(ent.label_)

        if target is not None and ent.text not in target:
            target.append(ent.text)

    return entities

def normalize_claim(cleaned: dict[str, Any]) -> ClaimNormalization:
    """
    Normalize a cleaned claim.

    """

    text = cleaned["cleaned_text"]

    doc = nlp(text)

    canonical_tokens = []

    for token in doc:

        if token.is_space or token.is_punct:
            continue

        canonical_tokens.append(token.lemma_)

    canonical = " ".join(canonical_tokens)

    fingerprint_tokens = []

    for token in doc:

        if (
            token.is_stop
            or token.is_punct
            or token.is_space
        ):
            continue

        fingerprint_tokens.append(token.lemma_.lower())

    fingerprint = " ".join(dict.fromkeys(fingerprint_tokens))

    keywords = list(
    dict.fromkeys(
        keyword
        for keyword, _ in keyword_extractor.extract_keywords(text)))
    numbers = []

    for token in doc:

        if token.like_num:
            numbers.append(token.text)

    dates = []

    for ent in doc.ents:

        if ent.label_ == "DATE":

            parsed = dateparser.parse(ent.text)

            if parsed:
                dates.append(
                    parsed.date().isoformat()
                )
            else:
                dates.append(ent.text)

    entities = _extract_entities(doc)

    entity_list = (
        entities.persons
        + entities.organizations
        + entities.locations
        + entities.events
        + entities.products
    )

    entity_string = " ".join(entity_list)

    tavily = text

    wikipedia = entity_string

    wikidata = entity_string
    action = ""

    for token in doc:
        if token.dep_ == "ROOT" and token.pos_ == "VERB":
            action = token.lemma_
            break
    gdelt = " ".join(filter(None,[entity_string,action,*dates,]))
    general = text

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

    doc = nlp(text)

    normalized_tokens = []

    for token in doc:

        if token.is_space:
            continue

        normalized_tokens.append(token.text)

    normalized_text = " ".join(normalized_tokens)

    normalized_text = re.sub(
        r"\s+([.,!?])",
        r"\1",
        normalized_text,
    )

    evidence.cleaned = normalized_text

    return evidence
