import pytest
from sqlmodel import Session, select

from app.core.rate_limit import get_rate_limiter
from app.db.models import CreatorPostAnalysisRecord, CreatorPostRecord
from app.db.session import engine, init_db


def _clear_creator_tables() -> None:
    with Session(engine) as session:
        for model in (CreatorPostAnalysisRecord, CreatorPostRecord):
            for row in session.exec(select(model)).all():
                session.delete(row)
        session.commit()


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    get_rate_limiter().reset()
    init_db()
    _clear_creator_tables()
    yield
    get_rate_limiter().reset()
    _clear_creator_tables()
