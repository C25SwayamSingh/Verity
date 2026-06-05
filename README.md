# Verity

**Verity** is a news and information integrity platform. Phase 1 (Core Checker MVP) lets users paste article or news text, run analysis, and receive structured results: summary, key takeaways, extracted claims with types, cross-source corroboration (fixture/mock sources), framing indicators, and a neutral rewrite.

This is **not** a “truth checker.” Results use careful language: cross-source corroboration, source alignment, credibility signals, framing indicators, and low corroboration — never absolute true/false verdicts.

## Repo structure

```
/verity
  /backend   — FastAPI, SQLite, analysis engine
  /frontend  — Next.js App Router UI
```

## Quick start

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Optional: set OPENAI_API_KEY for LLM-enhanced output; works without it (deterministic fallback)
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Open [http://localhost:3000](http://localhost:3000), paste text, choose a category, and click **Analyze**.

## Environment variables

| Variable | Where | Description |
|----------|--------|-------------|
| `OPENAI_API_KEY` | backend | Optional; enables OpenAI path when set |
| `OPENAI_MODEL` | backend | Default `gpt-4o-mini` |
| `DATABASE_URL` | backend | Default `sqlite:///./verity.db` |
| `RATE_LIMIT_ENABLED` | backend | Default `true` |
| `RATE_LIMIT_ANALYZE_REQUESTS` | backend | Default `5` |
| `RATE_LIMIT_ANALYZE_WINDOW_SECONDS` | backend | Default `3600` |
| `NEXT_PUBLIC_API_URL` | frontend | Backend base URL |

## API

- `GET /health` — health check
- `POST /v1/analyze` — run analysis on pasted text
- `GET /v1/analysis/{analysis_id}` — fetch stored result

## Phase 1 limitations

- Pasted text only (no video, batch, or scraping)
- Cross-source corroboration uses **mock/fixture** sources, not live news APIs
- No auth, billing, dashboards, study mode, or browser extension
- Eligibility engine may disable bias/framing for non-news content regardless of user-selected category

## Next phases (not built)

- Reliable News Dashboard
- Creator/Influencer Dashboard
- Batch video analysis
- Live source providers
- Billing, mobile app, browser extension

See `backend/README.md` and `frontend/README.md` for more detail.
