from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings

_settings = get_settings()
_connect_args = {"check_same_thread": False} if _settings.database_url.startswith("sqlite") else {}
engine = create_engine(_settings.database_url, connect_args=_connect_args)


def _ensure_creator_post_input_basis_column() -> None:
    """SQLite: add input_basis if DB predates Phase 3.11."""
    if not _settings.database_url.startswith("sqlite"):
        return
    import sqlite3

    path = _settings.database_url.replace("sqlite:///", "", 1)
    if path.startswith("./"):
        path = path[2:]
    conn = sqlite3.connect(path)
    try:
        cols = {row[1] for row in conn.execute("PRAGMA table_info(creator_post_records)")}
        if cols and "input_basis" not in cols:
            conn.execute(
                "ALTER TABLE creator_post_records "
                "ADD COLUMN input_basis TEXT DEFAULT 'third_party_extracted_key_points'"
            )
            conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    _ensure_creator_post_input_basis_column()


def get_session():
    with Session(engine) as session:
        yield session
