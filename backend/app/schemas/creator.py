from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.core.input_basis import DEFAULT_INPUT_BASIS, InputBasis


class WeakClaim(BaseModel):
    claim_id: str
    post_id: str
    text: str
    corroboration_status: str
    note: str


class CreatorOverview(BaseModel):
    creator_id: str
    name: str
    platform: str
    handle: str
    category: str
    bio: str
    metrics_source: str = "derived_from_analysis"
    total_analyzed_posts: int = Field(ge=0)
    source_alignment_score: float = Field(ge=0.0, le=1.0)
    claim_support_rate: float = Field(ge=0.0, le=1.0)
    contradiction_rate: float = Field(ge=0.0, le=1.0)
    low_corroboration_rate: float = Field(ge=0.0, le=1.0)
    source_diversity_score: float = Field(ge=0.0, le=1.0)
    average_framing_score: float = Field(ge=0.0, le=1.0)
    top_topics: list[str]
    most_used_sources: list[str]
    most_reliable_posts: list[str]
    weakest_claims: list[WeakClaim]
    transparency_summary: str


class CreatorListItem(BaseModel):
    creator_id: str
    name: str
    platform: str
    handle: str
    category: str
    bio: str
    metrics_source: str = "derived_from_analysis"
    total_analyzed_posts: int = Field(ge=0)
    source_alignment_score: float = Field(ge=0.0, le=1.0)
    claim_support_rate: float = Field(ge=0.0, le=1.0)
    contradiction_rate: float = Field(ge=0.0, le=1.0)
    top_topics: list[str]


class CreatorListResponse(BaseModel):
    creators: list[CreatorListItem]


class PostClaim(BaseModel):
    claim_id: str
    text: str
    claim_type: str
    corroboration_status: str


class CreatorPost(BaseModel):
    post_id: str
    creator_id: str
    title: str
    platform: str
    published_at: str
    source_url: str
    topic: str
    summary: str
    metrics_source: str = "derived_from_analysis"
    claims: list[PostClaim]
    supported_claims_count: int = Field(ge=0)
    contradicted_claims_count: int = Field(ge=0)
    low_corroboration_claims_count: int = Field(ge=0)
    source_alignment_score: float = Field(ge=0.0, le=1.0)
    framing_label: str
    sources_used: list[str]
    audience_signal_placeholder: str
    input_basis: Optional[str] = None
    input_basis_label: Optional[str] = None
    input_basis_note: Optional[str] = None


class CreatorPostsResponse(BaseModel):
    creator_id: str
    posts: list[CreatorPost]


class CreateDemoCreatorPostRequest(BaseModel):
    """Manual demo workflow: paste transcript or article text for a creator."""

    title: str = Field(min_length=1)
    content: str = Field(
        min_length=80,
        description="Full post, article, or transcript text to analyze (minimum 80 characters).",
    )
    topic: str = Field(min_length=1)
    platform: str = "manual"
    published_at: Optional[str] = None
    source_url: str = ""
    content_type: Literal["article", "transcript", "pasted_text"] = "transcript"
    input_basis: InputBasis = DEFAULT_INPUT_BASIS
    post_id: Optional[str] = None


class CreateDemoCreatorPostResponse(BaseModel):
    post: CreatorPost
    message: str
    analysis_persisted: bool = True
