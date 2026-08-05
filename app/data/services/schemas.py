from dataclasses import dataclass, field
from pydantic import BaseModel,Field

@dataclass(slots=True)
class Entities:
    persons: list[str] = field(default_factory=list)
    organizations: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    events: list[str] = field(default_factory=list)
    products: list[str] = field(default_factory=list)

@dataclass(slots=True)
class SearchQueries:
    general: str
    tavily: str
    wikipedia: str
    wikidata: str
    gdelt: str

@dataclass(slots=True)
class ClaimNormalization:
    original: str
    cleaned: str
    normalized: str
    canonical: str
    fingerprint: str

    entities: Entities = field(default_factory=Entities)
    keywords: list[str] = field(default_factory=list)
    numbers: list[str] = field(default_factory=list)
    dates: list[str] = field(default_factory=list)

    search_queries: SearchQueries | None = None

@dataclass(slots=True)
class Evidence:
    source: str
    url: str
    title: str
    raw_text: str
    text: str
    cleaned: str

@dataclass(slots=True)
class NLIResult:
    evidence: Evidence
    label: str
    confidence: float

@dataclass(slots=True)
class ScoreResult:
    verdict: str
    credibility_score: float
    explanation: str

class BatchNLIItem(BaseModel):
    id: int = Field(description="Index of the evidence in the batch.")
    label: str = Field(description="SUPPORTS, REFUTES or NEI")
    confidence: float = Field(description="Confidence between 0.0 and 1.0")


class BatchNLIResponse(BaseModel):
    results: list[BatchNLIItem]
