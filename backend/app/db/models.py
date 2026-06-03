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
