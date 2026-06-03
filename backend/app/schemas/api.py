from pydantic import BaseModel, Field

from app.schemas.domain import AnalyzeResponse, ContentType


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=20, max_length=50000)
    content_type: ContentType = ContentType.article
    user_selected_category: str = "domestic_us"


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "the-giver-api"


class RateLimitError(BaseModel):
    error: str = "rate_limit_exceeded"
    message: str
    retry_after_seconds: int


class AnalysisDetailResponse(AnalyzeResponse):
    pass
