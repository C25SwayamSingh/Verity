# PROJECT_STATE.md — The Giver

> Checkpoint for Cursor agents. Last updated: 2026-06-04. Phase 1–2 complete. Phase 3 complete. Phase 4A media upload MVP complete. Phase 4C ingestion correction complete (URL-only links no longer analyzed as content). 124 backend tests green; frontend build clean (7 routes).

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

**Phase 3 (Creator / Influencer Integrity Dashboard) — SCAFFOLD COMPLETE.**
- `GET /v1/creators` — list of creator profiles. ✓
- `GET /v1/creators/{creator_id}` — creator overview with integrity metrics. ✓
- `GET /v1/creators/{creator_id}/posts` — analyzed posts per creator. ✓
- Creator list UI at `/creators` with metric cards and integrity scores. ✓
- Creator detail UI at `/creators/[id]` with full metric breakdown, posts, weakest claims, transparency summary. ✓
- Nav link added to header. ✓
- 4 fixture creators (tech_ai, domestic_us, foreign_world, markets_stocks); 20 fixture posts total. ✓
- No real social media API connections; no auth; no monetization.

**Phase 3.5 (Creator metrics from analysis engine) — COMPLETE.**
- `IngestService.run_analysis()` — reusable pipeline without DB persist (HTTP `/v1/analyze` unchanged). ✓
- `CreatorMetricsService` — runs fixture post text through analysis; aggregates integrity metrics. ✓
- `CreatorService` — overview/list/posts metrics derived at request time; `metrics_source: derived_from_analysis`. ✓
- Post text built from optional `content` field or title + summary + fixture claim text. ✓
- 12 new backend tests in `test_creator_metrics.py`. ✓

**Phase 3.6 (Creator demo pipeline + persisted analyses) — COMPLETE.**
- SQLite tables: `creator_post_records`, `creator_post_analysis_records`. ✓
- Content-hash cache: reuse persisted analysis; recompute when post content changes. ✓
- `POST /v1/creators/{creator_id}/posts/demo` — manual demo workflow for transcripts/posts. ✓
- Demo guide: `docs/CREATOR_DEMO_WORKFLOW.md`. ✓
- 6 new backend tests in `test_creator_persistence.py`; 106 tests total green. ✓

**Phase 3.7 (Creator dashboard demo polish) — COMPLETE.**
- `/creators` and `/creators/[id]` UI polished for stakeholder demos. ✓
- Per-metric “what this means” helper copy (claim support, contradiction, low corroboration, source alignment, diversity, framing). ✓
- Sample integrity report layout on detail page (at-a-glance, transparency summary, claims needing attention). ✓
- Required disclaimer: measures alignment/support/framing; does not determine absolute truth. ✓
- Improved loading, empty, and error states with retry on creator pages. ✓
- No backend or API shape changes. ✓

**Phase 3.8 (Creator demo pack + outreach readiness) — COMPLETE.**
- `docs/CREATOR_OUTREACH_PACK.md` — creator-facing copy (measures / does not measure / why use / trust), outreach DM/email templates, stakeholder narrative, FAQ, pre-outreach checklist. ✓
- `docs/CREATOR_DEMO_SCRIPT.md` — 8–10 min live demo script (contrast path creator-003 vs creator-004), language cheat sheet, troubleshooting. ✓
- `docs/DEMO_CREATOR_PROFILES.md` — guide to four sample integrity profiles and when to use each in demos. ✓
- `docs/CREATOR_DEMO_WORKFLOW.md` — updated with Phase 3.8 doc index, recommended demo flow, deep links. ✓
- No backend, frontend, or fixture changes. ✓
- Tests/build: not re-run (documentation-only phase). ✓

**Phase 3.9 (Internal demo post form) — COMPLETE.**
- `/creators/demo` — internal-only form; submits to existing `POST /v1/creators/{creator_id}/posts/demo`. ✓
- Fields: creator ID, title, platform, original link, topic, optional summary (prepended to analyzable text), transcript/content, content type, optional post ID for updates. ✓
- Success state with link to `/creators/{id}`; clear error and loading states. ✓
- Links from `/creators` and `/creators/[id]`; `CreatorEmptyState` optional CTA. ✓
- `createDemoCreatorPost()` in `frontend/lib/api.ts`; types in `frontend/lib/types.ts`. ✓
- No backend or API shape changes; Phase 3.6 SQLite persistence unchanged. ✓

**Phase 4C (Core ingestion correction — URLs are not analyzable content) — COMPLETE.**
- **What was broken:** submitting only a social/video URL (e.g. an Instagram Reel link) made the checker analyze the URL *string* — summary, key takeaways, and the extracted claim were all the URL itself.
- **Fix:** new `backend/app/core/ingestion.py` classifies each checker submission and detects link-only input. A bare social/video (or other) URL is never treated as a claim.
- **Ingestion types:** `pasted_text`, `article_url`, `social_video_url`, `transcript_text`, `source_notes` (text endpoint) plus `uploaded_video/audio/screen_recording` (media endpoint, Phase 4A). Exposed on `AnalyzeResponse.ingestion` (`IngestionInfo`). ✓
- **URL-only behavior:** returns `ingestion.needs_more_input=true` with `guidance`; `summary` is a clear "no analyzable text" message; `key_takeaways=[]`, `claims=[]`, `neutral_rewrite=""`. The URL is kept in `ingestion.source_links` as metadata only — no download/scrape. ✓
- **Text + link:** when analyzable text is present, the text is analyzed and links are retained as source metadata (note added). ✓
- **Input basis values:** unchanged (`full_transcript`, `manual_rough_transcript`, `caption_text`, `third_party_extracted_key_points`, `manual_summary_source_notes`) plus media bases (`uploaded_video/audio/screen_recording_transcript`). ✓
- **Eligibility correction:** neutral/clearer rewrite is now available for **any** content with enough analyzable text (≥40 chars). Only full news bias/framing + cross-source corroboration remain gated to supported news categories (breaking, domestic_us, foreign_world, markets_stocks, tech_ai). ✓
- **Frontend:** results page renders a focused "transcript or upload required" state for link-only input; `CheckerInput` shows an inline hint for link-only text; `NeutralRewrite` shows a "Clearer rewrite" for non-news; homepage copy clarifies input options. ✓
- **Media/transcription:** upload→transcript→checker path (Phase 4A) preserved; transcripts skip link-only detection. Transcription remains a swappable adapter (`mock` default; `openai` Whisper optional); tests use the mock provider. ✓
- **Limitations:** no article-text extraction from article URLs yet (article-URL-only also returns "text required"); no social download/scrape; mock transcription is deterministic placeholder text.
- **Tests:** 124 passed (10 new in `test_ingestion.py`). **Frontend build:** passed. ✓

**Phase 4B (Single-input UX + installable PWA share target) — COMPLETE.**
- Homepage rebuilt to one clean input: paste text/link or attach audio/video, single **Analyze** button. ✓
- Category dropdown, title, original-link, and media-type fields removed (category auto-detected). ✓
- Deleted `ArticleInput.tsx` and `MediaUploadPanel.tsx`; new `components/CheckerInput.tsx`. ✓
- PWA: `public/manifest.webmanifest` with Web `share_target` (GET); `icon.svg`/`icon-maskable.svg`; PWA meta in `layout.tsx`. ✓
- `/` reads `?title=/?text=/?url=` to pre-fill and auto-run when shared text ≥40 chars. ✓
- iOS share-sheet via Apple Shortcut (Safari lacks Web Share Target); docs in `docs/PWA_SHARE.md`. ✓
- No backend changes; media upload still posts `media_kind=auto` (backend infers from extension). ✓
- **Frontend build:** passed. Backend tests unchanged (114). ✓

**Phase 4A (Media ingestion MVP — upload → transcript → analysis) — COMPLETE.**
- `POST /v1/analyze/media` — multipart upload (video/audio/screen recording). ✓
- Formats: mp4, mov, m4a, mp3, wav; max 50 MB (`MEDIA_MAX_UPLOAD_BYTES`). ✓
- Transcription adapter: `mock` (default, tests) or `openai` (Whisper when key set). ✓
- Video → audio via ffmpeg when not in mock mode; temp files only. ✓
- Transcript → `IngestService.analyze()` → `/results/[id]` with `media_source` metadata. ✓
- Core Checker `/` upload UI; transparency note on results. ✓
- `docs/MEDIA_UPLOAD.md` — formats, providers, social-video guidance. ✓
- **Tests:** 114 passed. **Frontend build:** passed. ✓

**Phase 3.11 (Demo input basis / non-verbatim transparency) — COMPLETE.**
- `input_basis` on demo posts: full transcript, rough transcript, caption, third-party key points (default), manual source notes. ✓
- Stored in `creator_post_records.input_basis`; returned on `CreatorPost` as `input_basis`, `input_basis_label`, `input_basis_note`. ✓
- `/creators/demo` form: input basis selector + Fofo-style guidance; default third-party extracted key points. ✓
- Post cards on `/creators/[id]` show amber note for non-verbatim input. ✓
- `docs/CREATOR_DEMO_WORKFLOW.md` — input basis table, Instagram/Fofo sample inputs (docs only). ✓
- Checker pipeline unchanged — analyzes submitted text only. ✓
- **Tests:** 108 passed. **Frontend build:** passed. ✓

**Phase 3.10 (Demo validation with sample creator profiles) — COMPLETE.**
- Validated three fictional demo personas: `creator-001` (tech_ai), `creator-002` (domestic_us), `creator-004` (markets_stocks). ✓
- Added full analyzable `content` to 15 fixture posts (5 per persona) for information-dense transcripts. ✓
- `docs/CREATOR_DEMO_VALIDATION.md` — checklist, what worked/confused, transparency clarity, wording review, demo-readiness verdict. ✓
- `backend/scripts/enrich_demo_validation_content.py` — reproducible content enrichment. ✓
- API/UI smoke: list, overview metrics, weakest claims, transparency summary, post cards render correctly. ✓
- No API shape changes; no frontend code changes. ✓
- **Tests:** 106 passed after fixture update. **Frontend build:** not re-run (no frontend files changed). ✓

**Phase 2 (Reliable News Dashboard) — COMPLETE.**
- `GET /v1/dashboard/articles?category=<cat>` — top-5 endpoint. ✓
- `GET /v1/dashboard/articles/{article_id}` — detail endpoint. ✓
- Dashboard list UI at `/dashboard` with category dropdown. ✓
- Article detail UI at `/dashboard/[id]`. ✓
- Provider interface (`DashboardNewsProvider` ABC) separates data sourcing from scoring. ✓
- `DASHBOARD_NEWS_PROVIDER=fixtures` (default) or `live` (real RSS, no API key, auto-fallback). ✓
- Live provider reads public RSS feeds: BBC News, NPR, BBC World, Reuters Business, TechCrunch. ✓
- No auth, no billing, no article persistence.

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

## 4. Completed features (Phase 1 + Phase 2 + Phase 3 scaffold)

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
- Creator integrity dashboard (Phase 3 + 3.5): list, detail, and posts endpoints; fixture creators and posts; metrics **derived** from `IngestService.run_analysis()` on post content (claim corroboration, framing, source publishers); `metrics_source: derived_from_analysis`

---

## 4. Backend endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check → `{"status":"ok"}` |
| `POST` | `/v1/analyze` | Run analysis. Body: `AnalyzeRequest`. Returns `AnalysisDetailResponse`. Rate-limited by IP. |
| `POST` | `/v1/analyze/media` | Upload media → transcribe → analyze. Multipart: `file`, `media_kind`, `user_selected_category`, optional `title`/`source_url`. Rate-limited by IP. |
| `GET` | `/v1/analysis/{analysis_id}` | Fetch previously stored analysis by UUID. Returns 404 if not found. |
| `GET` | `/v1/dashboard/articles?category=<cat>` | Returns top 5 scored articles for a supported category. Returns 422 for unsupported categories (including `other`). |
| `GET` | `/v1/dashboard/articles/{article_id}` | Returns one article by ID. Returns 404 if not found. Looks up via primary provider then fixtures fallback. |
| `GET` | `/v1/creators` | Returns list of creator profiles (`CreatorListResponse`). |
| `GET` | `/v1/creators/{creator_id}` | Returns creator overview with all integrity metrics (`CreatorOverview`). 404 if not found. |
| `GET` | `/v1/creators/{creator_id}/posts` | Returns analyzed posts for a creator (`CreatorPostsResponse`). 404 if creator not found. |
| `POST` | `/v1/creators/{creator_id}/posts/demo` | Add/update demo post content; runs analysis; persists result. 404 if creator not found. |

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
- `/dashboard` (`dashboard/page.tsx`) — Reliable News Dashboard; category dropdown + top-5 article cards with "View full detail →" links
- `/dashboard/[id]` (`dashboard/[id]/page.tsx`) — Article detail page; all scores, framing, claims, source corroboration, back link
- `/creators` (`creators/page.tsx`) — Creator list with metric helpers, disclaimer, methodology, retry on error
- `/creators/[id]` (`creators/[id]/page.tsx`) — Sample integrity report layout, at-a-glance signals, metric explanations, transparency summary, claims needing attention, analyzed posts
- `/creators/demo` (`creators/demo/page.tsx`) — Internal demo post form (Phase 3.9); not in main nav
- `layout.tsx` — root layout with nav links (Core Checker / Dashboard / Creators)

**Components** (`frontend/components/`)
- `ArticleInput.tsx` — textarea + content-type + category dropdowns
- `ClaimCard.tsx` — single claim with type badge, corroboration status, sources
- `DashboardArticleCard.tsx` — ranked article card with scores, framing label, claims, warnings, "View full detail →" link
- `ErrorState.tsx` — error display
- `FramingPanel.tsx` — framing indicators list + overall label
- `LoadingState.tsx` — loading spinner
- `NeutralRewrite.tsx` — displays neutral rewrite block
- `ResultsDashboard.tsx` — orchestrates all result panels
- `SourceAlignmentPanel.tsx` — supporting / contradicting source cards

- `CreatorDisclaimer.tsx` — required trust disclaimer (full + compact)
- `CreatorMetricBar.tsx` — metric bar with inline “what this means” help
- `CreatorEmptyState.tsx` — empty state for list/detail
- `lib/creatorDisplay.ts` — shared metric copy, corroboration/framing labels, disclaimer text

**Lib** (`frontend/lib/`)
- `api.ts` — typed fetch wrappers for backend (includes `getDashboardArticles`, `getDashboardArticle`, `getCreators`, `getCreator`, `getCreatorPosts`, `createDemoCreatorPost`)
- `types.ts` — TypeScript mirrors of backend schemas (includes `DashboardArticle`, `DashboardResponse`, `CreatorListItem`, `CreatorOverview`, `CreatorPost`, `CreatorPostsResponse`, `WeakClaim`, `PostClaim`)
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

- **Scope**: `POST /v1/analyze` and `POST /v1/analyze/media`
- **Algorithm**: IP-based in-memory sliding window (`InMemoryRateLimiter` in `app/core/rate_limit.py`)
- **Defaults**: 5 requests per 3600 seconds per IP
- **IP resolution**: `X-Forwarded-For` header (first value) → `request.client.host` → `"unknown"`
- **Response on limit**: HTTP 429 with `{"error":"rate_limit_exceeded","retry_after_seconds":N}` + `Retry-After` header
- **Toggle**: set `RATE_LIMIT_ENABLED=false` to disable entirely (useful in tests)
- **State**: in-process only; resets on server restart; not shared across workers

---

## 8c. Creator service architecture (Phase 3 + 3.5 + 3.6)

**Files** (`backend/app/`)
- `schemas/creator.py` — Pydantic schemas including `metrics_source`, `CreateDemoCreatorPostRequest`
- `services/creator_service.py` — fixture + DB demo posts; `_get_or_analyze_post()` with SQLite cache
- `services/creator_metrics_service.py` — `analyze_post()`, `aggregate_metrics()`, `build_creator_post()`
- `services/creator_analysis_store.py` — `compute_content_hash()`, get/save persisted analyses
- `services/creator_post_store.py` — CRUD for `creator_post_records` (demo posts)
- `services/ingest_service.py` — `run_analysis()` (no persist); `analyze()` persists via SQLite
- `db/models.py` — `CreatorPostRecord`, `CreatorPostAnalysisRecord`
- `providers/fixtures/creators.json` — 4 fixture creator profiles (identity/bio)
- `providers/fixtures/creator_posts.json` — 20 fixture posts; **creator-001/002/004** have full `content` on all 5 posts each (Phase 3.10)
- `docs/CREATOR_DEMO_WORKFLOW.md` — manual demo workflow
- `docs/CREATOR_DEMO_SCRIPT.md` — live stakeholder/creator demo script
- `docs/CREATOR_OUTREACH_PACK.md` — outreach templates + creator-facing explanations
- `docs/DEMO_CREATOR_PROFILES.md` — sample profile picker for demos
- `docs/CREATOR_DEMO_VALIDATION.md` — Phase 3.10 validation notes and demo-readiness checklist

**Metric derivation** (pooled across a creator's analyzed posts):
- `claim_support_rate` — share of checkable claims with medium/high corroboration
- `contradiction_rate` / `low_corroboration_rate` — share of checkable claims contradicted / low corroboration
- `source_alignment_score` — mean per-claim alignment (high=1.0, medium=0.75, low=0.35, contradicted=0.15)
- `source_diversity_score` — min(1.0, unique supporting publishers / 8)
- `average_framing_score` — mean framing label score (mostly_neutral=0.85, mixed=0.55, notable=0.25)
- `top_topics` / `most_used_sources` / `most_reliable_posts` / `weakest_claims` / `transparency_summary` — aggregated from analysis outputs

**Fixture creators**:
| creator_id | Name | Platform | Category |
|---|---|---|---|
| `creator-001` | Nova Rivera | YouTube | tech_ai |
| `creator-002` | Marcus Webb | Twitter/X & Substack | domestic_us |
| `creator-003` | Leila Okonkwo | Podcast & Substack | foreign_world |
| `creator-004` | DataDave | TikTok & YouTube | markets_stocks |

**Persistence flow**: For each post → SHA-256 content hash → lookup `creator_post_analysis_records` → on miss, `run_analysis()` → save JSON → aggregate metrics for dashboard.

**Tests**: `test_creators.py` (35) + `test_creator_metrics.py` (12) + `test_creator_persistence.py` (6).

---

## 8b. Dashboard provider architecture

**Files** (`backend/app/providers/`)
- `dashboard_base.py` — `DashboardNewsProvider` ABC; single method `fetch(category) -> list[dict]`
- `dashboard_fixtures_provider.py` — loads `dashboard_articles.json`; default provider
- `dashboard_live_provider.py` — live RSS implementation (BBC, NPR, Reuters, TechCrunch); raises `DashboardProviderError` on failure
- `dashboard_registry.py` — `get_dashboard_provider(settings)` factory; maps env var to provider class

**Flow (list)**: `main.py` → `DashboardService.get_top_articles(category)` → `provider.fetch(category)` → score + sort → top 5. Falls back to fixtures on `DashboardProviderError` / `NotImplementedError`.

**Flow (detail)**: `main.py` → `DashboardService.get_article_by_id(id)` → `provider.fetch_by_id(id)` → falls back to fixtures if primary provider raises or returns None → 404 if not found.

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
| `TRANSCRIPTION_PROVIDER` | backend | `mock` | `mock` (dev/tests) or `openai` (Whisper) |
| `MEDIA_MAX_UPLOAD_BYTES` | backend | `52428800` | 50 MB default |
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
#   tests/test_dashboard.py            — endpoint, scoring, sorting, provider arch, detail drilldown (53 total)
#   tests/test_creators.py             — creator list/detail/posts endpoints, 404s, metric ranges (35 total)
#   tests/test_creator_metrics.py      — derived metrics from analysis pipeline (12 total)
#   tests/test_creator_persistence.py    — SQLite cache, hash invalidation, demo POST (6 total)
#   tests/test_media_upload.py          — media upload, transcription mock, analysis pipeline (6 total)
# Total: 114 tests
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
- **Creator dashboard is fixture-only** — no real social media API, no scraping, no user accounts
- **Creator post text is fixture-sourced** — primary personas use full `content` transcripts; other posts may still use title/summary/claims; not live platform posts
- **Legacy `creators.json` metrics can mislead** — dashboard values are derived at runtime; see `CREATOR_DEMO_VALIDATION.md`
- **Creator analyses persisted in SQLite** — per-post cache with content-hash invalidation; aggregation still runs each request
- **Legacy metric fields in creators.json** — retained in fixtures but overridden at runtime by derived values
- **No public creator badges** — not yet implemented
- **Creator post claims are not persisted** — no DB connection; creator data exists only in fixture JSON
- **No creator search or filtering** — list endpoint returns all creators; no pagination, category filter, or text search
- **Demo post form is internal-only** — `/creators/demo` has no auth; not creator onboarding or a public feature
- **Media upload is user-provided files only** — no URL download; Instagram/TikTok links are metadata on upload form
- **Video upload needs ffmpeg** when `TRANSCRIPTION_PROVIDER` is not `mock`
- **No batch media upload** — single file per request
- **Uploaded video files not retained** — transcript + analysis stored in SQLite
- **No video ingestion** — `input_basis` labels what was pasted; The Giver does not watch/transcribe Reels unless user supplies a full transcript or upload
- **Outreach pack is documentation only** — no PDF export, share links, or CRM integration for creator outreach

---

## 14. Next planned phase

**Phase 4A — COMPLETE.** Candidates for next:
- Wire media upload into creator demo workflow (optional)
- Batch upload, media library (Phase 4B+)
- Creator pilot program: track 2–3 real paste-only transcripts with written consent (process, not product)
- Enrich `content` on `creator-003` (and remaining posts) for parity with validation trio
- Export/share transparency summary as PDF or static link (opt-in, no public directory)
- Add optional dedicated `content` field on all fixture posts for richer analysis input
- Add creator search, filtering by category, and pagination to the list endpoint
- Add public creator badges (opt-in transparency tier indicator)
- Improve live news provider score estimation (importance/relevance/diversity are fixed defaults today)
- Persistent dashboard article caching (live articles vanish on restart)
- Auth / billing
- Browser extension

Other future work (not scoped): batch video analysis, mobile app.

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
- **Creator analysis caching**: Per-post analyses persist in SQLite; multi-worker deployments share DB but may race on first analyze.
- **Creator component extraction**: Creator page UI components are inlined in page files. If the creator UI grows, extract shared components (`CreatorCard`, `PostCard`, `MetricBar`) into `frontend/components/`.
- **Creator data persistence**: Creator posts are currently fixture JSON only. A production version needs DB models for `Creator` and `CreatorPost` tables with a Alembic migration path.
