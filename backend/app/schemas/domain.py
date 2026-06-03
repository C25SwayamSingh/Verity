from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class ContentType(str, Enum):
    article = "article"
    transcript = "transcript"
    pasted_text = "pasted_text"


class UserCategory(str, Enum):
    breaking = "breaking"
    domestic_us = "domestic_us"
    foreign_world = "foreign_world"
    markets_stocks = "markets_stocks"
    tech_ai = "tech_ai"
    other = "other"


SUPPORTED_NEWS_CATEGORIES = {
    UserCategory.breaking,
    UserCategory.domestic_us,
    UserCategory.foreign_world,
    UserCategory.markets_stocks,
    UserCategory.tech_ai,
}


class ClaimType(str, Enum):
    factual_claim = "factual_claim"
    opinion = "opinion"
    advice = "advice"
    prediction = "prediction"
    personal_experience = "personal_experience"
    promotional_claim = "promotional_claim"
    unclear = "unclear"


class CorroborationStatus(str, Enum):
    high_corroboration = "high_corroboration"
    medium_corroboration = "medium_corroboration"
    low_corroboration = "low_corroboration"
    contradicted = "contradicted"
    not_checkable = "not_checkable"


class FramingIndicatorType(str, Enum):
    emotionally_loaded_language = "emotionally_loaded_language"
    one_sided_framing = "one_sided_framing"
    opinion_presented_as_fact = "opinion_presented_as_fact"
    missing_context = "missing_context"
    exaggerated_language = "exaggerated_language"


class FramingOverallLabel(str, Enum):
    mostly_neutral = "mostly_neutral"
    mixed_framing = "mixed_framing"
    notable_framing = "notable_framing"


class SourceRef(BaseModel):
    source_id: str
    title: str
    publisher: str
    url: str
    snippet: str
    relevance_score: float = Field(ge=0.0, le=1.0)


class ClaimResult(BaseModel):
    claim_id: str
    text: str
    claim_type: ClaimType
    corroboration_status: CorroborationStatus
    supporting_sources: list[SourceRef] = Field(default_factory=list)
    contradicting_sources: list[SourceRef] = Field(default_factory=list)
    explanation: str


class FramingIndicator(BaseModel):
    indicator_type: FramingIndicatorType
    description: str
    examples: list[str] = Field(default_factory=list)


class FramingResult(BaseModel):
    overall_label: FramingOverallLabel
    indicators: list[FramingIndicator] = Field(default_factory=list)


class EligibilityResult(BaseModel):
    bias_framing_eligible: bool
    detected_category: str
    reason: str


class AnalyzeResponse(BaseModel):
    analysis_id: str
    summary: str
    key_takeaways: list[str]
    claims: list[ClaimResult]
    framing: FramingResult
    neutral_rewrite: str
    eligibility: EligibilityResult
    notes: list[str] = Field(default_factory=list)
