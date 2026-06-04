from pydantic import BaseModel, Field


class CorroborationSignal(BaseModel):
    level: str  # strong | moderate | limited | single_source
    label: str
    strength: float = Field(ge=0.0, le=1.0)
    detail: str = ""


class ContradictionSignal(BaseModel):
    present: bool
    label: str
    detail: str = ""


class FramingSignal(BaseModel):
    level: str  # neutral | mixed | notable | unknown
    label: str


class ConfidenceSignal(BaseModel):
    level: str  # high | medium | low
    label: str
    score: float = Field(ge=0.0, le=1.0)


class ScoreExplanation(BaseModel):
    key: str
    label: str
    weight: float
    weighted: bool
    description: str


class NewsFeedItem(BaseModel):
    id: str
    headline: str
    source: str
    category: str
    published_at: str
    neutral_summary: str

    # Composite ranking + components (kept for transparency).
    final_score: float = Field(ge=0.0, le=1.0)
    importance_score: float = Field(ge=0.0, le=1.0)
    credibility_score: float = Field(ge=0.0, le=1.0)
    relevance_score: float = Field(ge=0.0, le=1.0)
    freshness_score: float = Field(ge=0.0, le=1.0)
    source_diversity_score: float = Field(ge=0.0, le=1.0)

    # Derived integrity signals (non-weighted; surfaced under each headline).
    corroboration: CorroborationSignal
    contradiction: ContradictionSignal
    framing: FramingSignal
    confidence: ConfidenceSignal

    key_claims: list[str]
    why_selected: str
    detail_path: str


class NewsFeedResponse(BaseModel):
    category: str
    provider_mode: str
    generated_at: str
    items: list[NewsFeedItem]
    score_explanations: list[ScoreExplanation]
    disclaimer: str


class ScoringMethodResponse(BaseModel):
    formula: str
    weights: dict[str, float]
    score_explanations: list[ScoreExplanation]
    disclaimer: str
