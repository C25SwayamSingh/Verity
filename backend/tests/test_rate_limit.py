from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.rate_limit import get_rate_limiter
from app.db.session import init_db
from app.main import app

client = TestClient(app)

TEXT = (
    "The Federal Reserve left interest rates unchanged according to officials. "
    "Markets reacted as investors weighed inflation data from the Labor Department report."
)


def setup_function():
    init_db()
    get_rate_limiter().reset()


def test_rate_limit_returns_429(monkeypatch):
    get_rate_limiter().reset()
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("RATE_LIMIT_ANALYZE_REQUESTS", "2")
    monkeypatch.setenv("RATE_LIMIT_ANALYZE_WINDOW_SECONDS", "3600")
    get_settings.cache_clear()

    payload = {
        "text": TEXT,
        "content_type": "article",
        "user_selected_category": "domestic_us",
    }
    assert client.post("/v1/analyze", json=payload).status_code == 200
    assert client.post("/v1/analyze", json=payload).status_code == 200
    r = client.post("/v1/analyze", json=payload)
    assert r.status_code == 429
    body = r.json()
    assert body["error"] == "rate_limit_exceeded"
    assert "retry_after_seconds" in body
