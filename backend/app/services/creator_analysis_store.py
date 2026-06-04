"""SQLite persistence for creator post analyses with content-hash invalidation."""

import hashlib
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Session, select

from app.db.models import CreatorPostAnalysisRecord
from app.schemas.domain import AnalyzeResponse


def compute_content_hash(content: str) -> str:
    normalized = "\n".join(line.strip() for line in content.strip().splitlines())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def get_persisted_analysis(
    session: Session,
    post_id: str,
    content_hash: str,
) -> Optional[AnalyzeResponse]:
    record = session.get(CreatorPostAnalysisRecord, post_id)
    if record is None or record.content_hash != content_hash:
        return None
    return AnalyzeResponse.model_validate_json(record.result_json)


def save_persisted_analysis(
    session: Session,
    post_id: str,
    creator_id: str,
    content_hash: str,
    category: str,
    content_type: str,
    analysis: AnalyzeResponse,
) -> None:
    record = session.get(CreatorPostAnalysisRecord, post_id)
    payload = analysis.model_dump_json()
    if record is None:
        record = CreatorPostAnalysisRecord(
            post_id=post_id,
            creator_id=creator_id,
            content_hash=content_hash,
            content_type=content_type,
            category=category,
            result_json=payload,
        )
    else:
        record.content_hash = content_hash
        record.content_type = content_type
        record.category = category
        record.result_json = payload
        record.analyzed_at = datetime.now(timezone.utc)
    session.add(record)
    session.commit()


def delete_analysis_for_post(session: Session, post_id: str) -> None:
    record = session.get(CreatorPostAnalysisRecord, post_id)
    if record:
        session.delete(record)
        session.commit()


def delete_analyses_for_creator(session: Session, creator_id: str) -> None:
    records = session.exec(
        select(CreatorPostAnalysisRecord).where(
            CreatorPostAnalysisRecord.creator_id == creator_id
        )
    ).all()
    for record in records:
        session.delete(record)
    session.commit()
