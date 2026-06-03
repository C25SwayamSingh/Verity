# The Giver — Backend

FastAPI service for Phase 1 pasted-text information integrity analysis.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.db.init_db
uvicorn app.main:app --reload --port 8000
```

## Tests

```bash
pytest -q
```

## Environment

| Variable | Default | Notes |
|----------|---------|-------|
| `OPENAI_API_KEY` | (empty) | Deterministic heuristics when unset |
| `OPENAI_MODEL` | `gpt-4o-mini` | |
| `DATABASE_URL` | `sqlite:///./the_giver.db` | |
| `RATE_LIMIT_ENABLED` | `true` | |
| `RATE_LIMIT_ANALYZE_REQUESTS` | `5` | Per IP per window |
| `RATE_LIMIT_ANALYZE_WINDOW_SECONDS` | `3600` | |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated |

## Engine flow

1. Clean text → sentences → claim extraction & typing  
2. Content eligibility (text-based category detection)  
3. Fixture mock cross-source alignment (if eligible)  
4. Framing indicators & neutral rewrite (if eligible)  
5. Persist to SQLite → JSON response  

## Limitations

- Fixture sources only (no live news APIs)  
- IP rate limit on `POST /v1/analyze`  
- No authentication  
