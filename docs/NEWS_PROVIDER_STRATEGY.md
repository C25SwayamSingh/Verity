# News Provider Strategy — The Giver

How The Giver sources the stories shown in the **News Integrity Feed** (home
page) and the **Reliable News Dashboard**. The goal is one clean, swappable
provider path that prefers open/free/demo-friendly sources, never crashes when a
key is missing, and always falls back to fixtures.

## Architecture

All providers implement one interface — `DashboardNewsProvider`
(`backend/app/providers/dashboard_base.py`):

```python
class DashboardNewsProvider(ABC):
    def fetch(self, category: str) -> list[dict]: ...      # required
    def fetch_by_id(self, article_id: str) -> dict | None  # optional
```

- `DashboardService` selects the active provider via
  `get_dashboard_provider(settings)` (`dashboard_registry.py`), keyed off
  `DASHBOARD_NEWS_PROVIDER`.
- `DashboardService` **scores, sorts, and limits**; providers only return raw,
  normalized article dicts. One scoring formula lives in `core/news_scoring.py`.
- `NewsFeedService` wraps `DashboardService` and adds the derived integrity
  signals for the feed. It performs **no network calls of its own**.
- On any `DashboardProviderError` / `NotImplementedError`, `DashboardService`
  logs a warning and falls back to `DashboardFixturesProvider`. The app never
  crashes on a provider failure.

### Normalized article schema

Every provider returns dicts with at least:

```
id, headline, source, category, published_at, neutral_summary,
importance_score, credibility_score, relevance_score, freshness_score,
source_diversity_score, framing_label, key_claims, support_summary,
contradiction_warnings, why_selected
```

## Providers available now

| `DASHBOARD_NEWS_PROVIDER` | Source | API key | Notes |
|---|---|---|---|
| `fixtures` (default) | Local JSON (`fixtures/dashboard_articles.json`) | none | Offline, deterministic, used by all tests. |
| `live` | Public RSS (BBC, NPR, BBC World, Reuters Business, TechCrunch) | none | Headlines + time real; scores estimated. Falls back to fixtures on failure. |
| `gdelt` | GDELT 2.0 DOC API (open global news index) | none | Per-category query; credibility from domain prior, freshness from seen-date. Falls back to fixtures on failure. |

Both `live` and `gdelt` are **open and key-free**. They supply
headline/source/time but not real corroboration scores yet (see
`SCORING_METHOD.md`).

## Providers planned / later (not implemented)

These require licensed credentials or an official API and are **documented only**.
None are integrated; the app does not depend on them. Optional env keys exist
(`NEWSAPI_API_KEY`, `GNEWS_API_KEY`, `GOOGLE_FACTCHECK_API_KEY`) and default to
empty so nothing breaks when unset.

| Provider | Status | Why deferred |
|---|---|---|
| NewsAPI / GNews / WorldNewsAPI | optional, key-gated | Free tiers exist but require a key; only enable behind an env flag + key. |
| Google Fact Check Tools API | optional, key-gated | Useful for claim-level fact-check lookups; needs an API key. |
| Reuters / AP | licensed/commercial | **Do not assume free.** High-quality but paid. Add only with explicit licensed credentials. |
| Ground News | not planned | No official open API; do not depend on it. |

### How to add a licensed/keyed provider later

1. Add the key to `Settings` in `core/config.py` (default `""`) and to
   `.env.example`.
2. Create `dashboard_<name>_provider.py` implementing `DashboardNewsProvider`.
   Read the key from settings; if it is empty, raise `DashboardProviderError`
   (so the service falls back to fixtures) — **never** crash.
3. Normalize the API response into the schema above.
4. Register it in `dashboard_registry.py`.
5. Add tests that **mock the network seam** (`_fetch_raw`) — no live calls in CI.
6. Document it in this file.

## Requirements honored

- No hardcoded API keys; environment-variable configuration only.
- Missing keys do not crash the app (optional keys default to empty).
- Provider failures fall back to fixtures safely.
- Tests never depend on external network calls (the `_fetch_raw` seam is patched).
- Live providers parse defensively and raise `DashboardProviderError` on any
  fetch/parse error.
