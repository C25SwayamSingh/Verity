from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class AnalysisRecord(SQLModel, table=True):
    __tablename__ = "analysis_records"

    id: str = Field(primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    request_text: str
    content_type: str
    user_selected_category: str
    result_json: str


class CreatorPostRecord(SQLModel, table=True):
    """Manually added demo creator post content (not live platform ingestion)."""

    __tablename__ = "creator_post_records"

    post_id: str = Field(primary_key=True)
    creator_id: str = Field(index=True)
    title: str
    platform: str
    published_at: str
    source_url: str = ""
    topic: str
    content: str
    content_type: str = "transcript"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CreatorPostAnalysisRecord(SQLModel, table=True):
    """Persisted integrity analysis for a creator post, keyed by content hash."""

    __tablename__ = "creator_post_analysis_records"

    post_id: str = Field(primary_key=True)
    creator_id: str = Field(index=True)
    content_hash: str
    content_type: str
    category: str
    result_json: str
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
