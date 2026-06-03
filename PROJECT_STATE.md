# PROJECT_STATE.md — The Giver

> Checkpoint for Cursor agents. Last updated: 2026-06-03. Phase 1 complete. Phase 2 scaffold + live RSS provider complete. 41 backend tests green; frontend builds clean.

---

## 1. Product name and purpose

**The Giver** — a news and information integrity platform.  
Users paste article or transcript text; the engine returns a structured integrity report: summary, key takeaways, typed claims with cross-source corroboration, framing indicators, and a neutral rewrite.  
Language is deliberately non-verdictive ("low corroboration", "notable framing") — never "true/false."

---

## 2. Current phase status

**Phase 1 (Core Checker MVP) — COMPLETE. All tests green.**
- Backend: FastAPI + SQLite, deterministic heuristics with optional OpenAI enhancement.
- Frontend: Next.js 15 App Router, Tailwind CSS.
- No auth, billing, or live data sources.

**Phase 2 (Reliable News Dashboard) — IN PROGRESS (scaffold + provider architecture + live RSS provider complete).**
- `GET /v1/dashboard/articles?category=<cat>` endpoint live.
- Fixture-ranked top-5 articles per category.
- Dashboard UI at `/dashboard` with category dropdown.
- Provider interface (`DashboardNewsProvider` ABC) separates data sourcing from scoring.
- `DASHBOARD_NEWS_PROVIDER=fixtures` (default) or `live` (real RSS, no API key, auto-fallback to fixtures on failure).
- Live provider reads public RSS feeds: BBC News, NPR, BBC World, Reuters Business, TechCrunch.
- No auth, no drilldown, no article persistence yet.

---

## 3. Phase 2 — Dashboard scoring formula

```
final_score = 0.35 × importance_score
            + 0.30 × credibility_score
            + 0.20 × relevance_score
            + 0.10 × freshness_score
            + 0.05 × source_diversity_score
```

All component scores are 0–1. Computed dynamically in `DashboardService`; stored as `final_score` in the response. Fixture data lives in `backend/app/providers/fixtures/dashboard_articles.json` (30 articles, 6 per category).

## 4. Completed features (Phase 1 + Phase 2 scaffold)

- Paste text → structured integrity analysis
- Content-type selection (`article`, `transcript`, `pasted_text`)
- User category selection (`breaking`, `domestic_us`, `foreign_world`, `markets_stocks`, `tech_ai`, `other`)
- Automatic category detection with keyword scoring
- Eligibility routing (disables bias/framing for non-news content)
- Claim extraction + typing (7 types)
- Fixture-based cross-source alignment / corroboration (mock sources, no live API)
- Framing indicators (5 types) + overall label (3 levels)
- Neutral rewrite
- SQLite persistence of each analysis by UUID
- IP-based in-memory sliding-window rate limiting on `POST /v1/analyze`
- OpenAI path (optional) for summary + claims + framing + rewrite; deterministic fallback when key absent

---

## 4. Backend endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check → `{"status":"ok"}` |
| `POST` | `/v1/analyze` | Run analysis. Body: `AnalyzeRequest`. Returns `AnalysisDetailResponse`. Rate-limited by IP. |
| `GET` | `/v1/analysis/{analysis_id}` | Fetch previously stored analysis by UUID. Returns 404 if not found. |
| `GET` | `/v1/dashboard/articles?category=<cat>` | Returns top 5 fixture-ranked articles for a supported category. Returns 422 for unsupported categories (including `other`). |

**Request schema (`AnalyzeRequest`)**
```
text: str
content_type: "article" | "transcript" | "pasted_text"
user_selected_category: "breaking" | "domestic_us" | "foreign_world" | "markets_stocks" | "tech_ai" | "other"
```

**Response schema (`AnalysisDetailResponse` / `AnalyzeResponse`)**
```
analysis_id, summary, key_takeaways[], claims[], framing, neutral_rewrite, eligibility, notes[]
```

---

## 5. Frontend pages / components

**Pages** (`frontend/app/`)
- `/` (`page.tsx`) — text input form, category selector, analyze button
- `/results/[id]` — renders stored analysis fetched from `GET /v1/analysis/{id}`
- `/dashboard` (`dashboard/page.tsx`) — Reliable News Dashboard; category dropdown + top-5 article cards
- `layout.tsx` — root layout with nav links (Core Checker / Dashboard)

**Components** (`frontend/components/`)
- `ArticleInput.tsx` — textarea + content-type + category dropdowns
- `ClaimCard.tsx` — single claim with type badge, corroboration status, sources
- `DashboardArticleCard.tsx` — ranked article card with scores, framing label, claims, warnings
- `ErrorState.tsx` — error display
- `FramingPanel.tsx` — framing indicators list + overall label
- `LoadingState.tsx` — loading spinner
- `NeutralRewrite.tsx` — displays neutral rewrite block
- `ResultsDashboard.tsx` — orchestrates all result panels
- `SourceAlignmentPanel.tsx` — supporting / contradicting source cards

**Lib** (`frontend/lib/`)
- `api.ts` — typed fetch wrappers for backend (includes `getDashboardArticles`)
- `types.ts` — TypeScript mirrors of backend schemas (includes `DashboardArticle`, `DashboardResponse`)
- `color.ts` — corroboration/framing color utilities

---

## 6. Engine flow (backend)

```
IngestService.analyze()
  1. SentenceService.process(text)         → cleaned text + sentence list
  2. _detect_category(text, user_selected) → detected category (keyword scoring; non-news keywords short-circuit to "other")
  3. _is_bias_framing_eligible(...)        → bool (requires supported news category, ≥80 chars, no non-news keywords)
  4. _build_eligibility(...)               → EligibilityResult with reason string
  5. _summarize(text, eligible)            → summary, key_takeaways, notes  [OpenAI or deterministic]
  6. ClaimService.extract(sentences, text) → raw claims  [OpenAI or heuristic]
  7. SourceAlignmentService.align_claims() → ClaimResult[] with fixture corroboration
  8. FramingService.analyze(text, eligible)→ FramingResult  [OpenAI or heuristic; skipped if ineligible]
  9. RewriteService.neutral_rewrite(...)   → neutral rewrite string  [OpenAI or passthrough if ineligible]
 10. Persist AnalysisRecord to SQLite
 11. Return AnalyzeResponse (JSON)
```

**Providers**: `FixturesProvider` (category-keyed fixture JSON) and `MockProvider` (random fallback) back `SourceAlignmentService`. No live news APIs.

---

## 7. Eligibility router behavior

`_is_bias_framing_eligible` returns `True` only when ALL of the following hold:

1. Detected category is NOT `other`
2. Detected category is in `SUPPORTED_NEWS_CATEGORIES` (`breaking`, `domestic_us`, `foreign_world`, `markets_stocks`, `tech_ai`)
3. No `NON_NEWS_KEYWORDS` match (e.g. "recipe", "gameplay", "workout plan")
4. Text length ≥ 80 characters after cleaning

When `False`:
- `framing` returns a neutral/empty result
- `neutral_rewrite` returns a passthrough or minimal stub
- Fixture corroboration still runs but uses `user_selected_category` as the key instead of the detected category
- `eligibility.reason` explains why in plain English (3 distinct reason strings)

---

## 8. Rate limiting behavior

- **Scope**: `POST /v1/analyze` only
- **Algorithm**: IP-based in-memory sliding window (`InMemoryRateLimiter` in `app/core/rate_limit.py`)
- **Defaults**: 5 requests per 3600 seconds per IP
- **IP resolution**: `X-Forwarded-For` header (first value) → `request.client.host` → `"unknown"`
- **Response on limit**: HTTP 429 with `{"error":"rate_limit_exceeded","retry_after_seconds":N}` + `Retry-After` header
- **Toggle**: set `RATE_LIMIT_ENABLED=false` to disable entirely (useful in tests)
- **State**: in-process only; resets on server restart; not shared across workers

---

## 8b. Dashboard provider architecture

**Files** (`backend/app/providers/`)
- `dashboard_base.py` — `DashboardNewsProvider` ABC; single method `fetch(category) -> list[dict]`
- `dashboard_fixtures_provider.py` — loads `dashboard_articles.json`; default provider
- `dashboard_live_provider.py` — live RSS implementation (BBC, NPR, Reuters, TechCrunch); raises `DashboardProviderError` on failure
- `dashboard_registry.py` — `get_dashboard_provider(settings)` factory; maps env var to provider class

**Flow**: `main.py` → `DashboardService()` → `get_dashboard_provider(settings)` → returns provider → `service.get_top_articles()` calls `provider.fetch(category)`. If the provider raises `DashboardProviderError` or `NotImplementedError`, the service logs a warning and falls back to `DashboardFixturesProvider`.

**Live provider** (`DashboardLiveProvider`, Phase 2.7): fetches public RSS feeds via `httpx`, parses with `feedparser`. Estimates `credibility_score` from source name, `freshness_score` from publication age. Fixed defaults for `importance` / `relevance` / `source_diversity` until a scoring model is added.

**To enable live**: set `DASHBOARD_NEWS_PROVIDER=live` in `.env` and restart. No endpoint, schema, scoring, or frontend changes required. Falls back to fixtures automatically on any network/parse failure.

## 9. Environment variables

| Variable | Service | Default | Notes |
|----------|---------|---------|-------|
| `OPENAI_API_KEY` | backend | `""` | Deterministic heuristics when empty |
| `OPENAI_MODEL` | backend | `gpt-4o-mini` | |
| `DATABASE_URL` | backend | `sqlite:///./the_giver.db` | |
| `RATE_LIMIT_ENABLED` | backend | `true` | Set `false` to disable |
| `RATE_LIMIT_ANALYZE_REQUESTS` | backend | `5` | Per IP per window |
| `RATE_LIMIT_ANALYZE_WINDOW_SECONDS` | backend | `3600` | |
| `CORS_ORIGINS` | backend | `http://localhost:3000` | Comma-separated list |
| `DASHBOARD_NEWS_PROVIDER` | backend | `fixtures` | `fixtures` (JSON) or `live` (RSS, no API key) |
| `NEXT_PUBLIC_API_URL` | frontend | `http://localhost:8000` | Backend base URL |

Backend reads from `backend/.env` (copy from `backend/.env.example`).  
Frontend reads from `frontend/.env.local` (copy from `frontend/.env.example`).

---

## 10. Commands to run backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # edit OPENAI_API_KEY if desired
python -m app.db.init_db         # optional: explicit DB init (also runs on startup)
uvicorn app.main:app --reload --port 8000
```

---

## 11. Commands to run frontend

```bash
cd frontend
npm install
cp .env.example .env.local       # set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev                      # http://localhost:3000
```

---

## 12. Commands to run tests

```bash
# Backend (from backend/ with venv active)
cd backend
source .venv/bin/activate
pytest -q

# Test files:
#   tests/test_analyze_integration.py  — full analyze pipeline (no OpenAI)
#   tests/test_claims.py               — claim extraction/typing
#   tests/test_rate_limit.py           — rate limiter logic
#   tests/test_scoring.py              — scoring utilities
#   tests/test_dashboard.py            — dashboard endpoint, scoring formula, sorting, provider architecture (41 total)
```

No frontend test suite exists yet.

---

## 13. Known limitations

- **Pasted text only** — no URL scraping, batch upload, or video
- **Fixture/mock corroboration** — cross-source alignment uses static JSON fixtures, not live news APIs
- **No authentication** — any client can call the API
- **No billing or usage tracking** — only coarse IP rate limiting
- **No browser extension, mobile app, or study mode**
- **Rate limiter is in-process** — not safe for multi-worker deployments; resets on restart
- **OpenAI path untested in CI** — tests run with `OPENAI_API_KEY` unset (deterministic path only)
- **Category detection is keyword-only** — no ML classifier; can misdetect mixed-content text

---

## 14. Next planned phase

**Phase 2 — Reliable News Dashboard** (scaffold + live RSS provider complete; refinement remaining):
- Scaffold: fixture-ranked top-5 articles per category, dashboard UI at `/dashboard`. ✓
- Provider architecture: ABC + fixtures + live RSS provider + registry + env var. ✓
- Live provider: BBC News, NPR, BBC World, Reuters Business, TechCrunch RSS (no API key). ✓
- Remaining: Improve live provider score estimation (importance, relevance, source diversity are fixed defaults)
- Remaining: Article detail drilldown page
- Remaining: Persistence/caching layer for fetched articles

Other future work (not scoped): Creator/Influencer Dashboard, batch video analysis, browser extension, billing, mobile app.

---

## 15. Open decisions

- **Source provider upgrade**: Live provider currently uses free public RSS. Replacing with a structured news API (NewsAPI, Guardian, GDELT) would improve article metadata and score quality.
- **Auth strategy**: Session vs. JWT; whether Phase 2 requires login or stays public.
- **Rate limiter scaling**: Replace in-memory limiter with Redis before any multi-worker deployment.
- **Live provider score quality**: `importance_score`, `relevance_score`, `source_diversity_score` are fixed defaults in the live provider. Real scoring requires NLP or a paid signals API.
- **RSS feed reliability**: public RSS URLs (BBC, NPR, Reuters, TechCrunch) can change or go offline; no monitoring or fallback-URL list exists yet.
- **Frontend tests**: No test suite exists; Vitest + React Testing Library vs. Playwright E2E not chosen.
- **OpenAI model pinning**: `gpt-4o-mini` is the default; no fallback model if it is deprecated.
- **DB migrations**: SQLite + SQLModel with no Alembic setup; schema changes require manual migration.
