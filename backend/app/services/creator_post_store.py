"""Persistence for manually added demo creator posts."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Session, select

from app.core.input_basis import DEFAULT_INPUT_BASIS
from app.db.models import CreatorPostRecord


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def record_to_post_dict(record: CreatorPostRecord) -> dict:
    return {
        "post_id": record.post_id,
        "creator_id": record.creator_id,
        "title": record.title,
        "platform": record.platform,
        "published_at": record.published_at,
        "source_url": record.source_url,
        "topic": record.topic,
        "content": record.content,
        "content_type": record.content_type,
        "input_basis": getattr(record, "input_basis", None) or DEFAULT_INPUT_BASIS,
        "claims": [],
        "audience_signal_placeholder": (
            "Engagement rate and comment sentiment data not yet collected."
        ),
    }


def list_demo_posts(session: Session, creator_id: str) -> list[dict]:
    records = session.exec(
        select(CreatorPostRecord)
        .where(CreatorPostRecord.creator_id == creator_id)
        .order_by(CreatorPostRecord.created_at)
    ).all()
    return [record_to_post_dict(r) for r in records]


def get_demo_post(session: Session, post_id: str) -> Optional[CreatorPostRecord]:
    return session.get(CreatorPostRecord, post_id)


def create_demo_post(
    session: Session,
    creator_id: str,
    *,
    title: str,
    content: str,
    topic: str,
    platform: str = "manual",
    published_at: Optional[str] = None,
    source_url: str = "",
    content_type: str = "transcript",
    input_basis: str = DEFAULT_INPUT_BASIS,
    post_id: Optional[str] = None,
) -> dict:
    pid = post_id or f"demo-{uuid.uuid4().hex[:12]}"
    existing = session.get(CreatorPostRecord, pid)
    now = datetime.now(timezone.utc)
    if existing:
        existing.title = title
        existing.platform = platform
        existing.published_at = published_at or existing.published_at
        existing.source_url = source_url
        existing.topic = topic
        existing.content = content
        existing.content_type = content_type
        existing.input_basis = input_basis
        existing.updated_at = now
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return record_to_post_dict(existing)

    record = CreatorPostRecord(
        post_id=pid,
        creator_id=creator_id,
        title=title,
        platform=platform,
        published_at=published_at or _now_iso(),
        source_url=source_url,
        topic=topic,
        content=content,
        content_type=content_type,
        input_basis=input_basis,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record_to_post_dict(record)
