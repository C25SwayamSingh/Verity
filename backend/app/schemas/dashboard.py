from pydantic import BaseModel, Field


class DashboardArticle(BaseModel):
    id: str
    headline: str
    source: str
    category: str
    published_at: str
    neutral_summary: str
    importance_score: float = Field(ge=0.0, le=1.0)
    credibility_score: float = Field(ge=0.0, le=1.0)
    relevance_score: float = Field(ge=0.0, le=1.0)
    freshness_score: float = Field(ge=0.0, le=1.0)
    source_diversity_score: float = Field(ge=0.0, le=1.0)
    final_score: float = Field(ge=0.0, le=1.0)
    framing_label: str
    key_claims: list[str]
    support_summary: str
    contradiction_warnings: list[str]
    why_selected: str


class DashboardResponse(BaseModel):
    category: str
    articles: list[DashboardArticle]
