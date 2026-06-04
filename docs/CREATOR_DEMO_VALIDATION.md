# Creator Demo Validation — Phase 3.10

Validation of whether **sample integrity profiles** support realistic, controlled demos. All personas are **fictional** (permission-safe demo names only).

**Validated:** 2026-06-04 · **Backend tests:** 106 passed after fixture enrichment

---

## Sample creators tested

| Creator ID | Fictional name | Category | Demo role |
|------------|----------------|----------|-----------|
| `creator-001` | Nova Rivera | `tech_ai` | AI / tech news explainer |
| `creator-002` | Marcus Webb | `domestic_us` | U.S. politics / current events |
| `creator-004` | DataDave | `markets_stocks` | Finance / markets commentary |

**Not in primary trio (reference only):** `creator-003` Leila Okonkwo (`foreign_world`) — strong **source transparency** contrast; still useful for side-by-side demos per `DEMO_CREATOR_PROFILES.md`.

---

## Content used

- **15 fixture posts** updated with full `content` fields (5 per creator above) in `backend/app/providers/fixtures/creator_posts.json`.
- Each `content` block is an information-dense transcript-style passage (80+ characters), citing plausible sources (SEC, Federal Reserve, Congressional Record, EUR-Lex, ArXiv, etc.).
- Posts retain existing titles, summaries, and display metadata; analysis runs on `content` via `post_content()` (Phase 3.5+).
- Categories align with engine eligibility: `tech_ai`, `domestic_us`, `markets_stocks`.
- Enrichment script (reproducible): `backend/scripts/enrich_demo_validation_content.py`.

**Post themes (examples):**

- **Nova Rivera:** EU AI Act, coding models, federated learning, open vs closed AI safety, transformers.
- **Marcus Webb:** voting rights bill, federal budget, Federal Register timing, media coverage counts, gerrymandering precedent.
- **DataDave:** earnings basics, chart-pattern hype, CPI methodology skepticism, bank crash thread, Fed dual mandate.

---

## Validation checklist

| Check | Result |
|-------|--------|
| `GET /v1/creators` lists all profiles | Pass |
| `GET /v1/creators/{id}` returns metrics + transparency summary | Pass |
| `GET /v1/creators/{id}/posts` returns post cards with claims | Pass |
| `metrics_source: derived_from_analysis` on posts | Pass |
| Weakest claims populated when low corroboration / contradiction present | Pass |
| `/creators` list UI (manual smoke) | Pass — cards load with metric helpers |
| `/creators/[id]` detail UI (manual smoke) | Pass — at-a-glance, summary, claims, posts |
| `/creators/demo` form still available | Pass — unchanged |
| Language avoids “truth score” / “fake news” / “bad creator” | Pass — UI copy from Phase 3.7 |

**API snapshot after enrichment (derived metrics, illustrative):**

| Creator | Posts | Claim support | Low corroboration | Source alignment |
|---------|-------|---------------|-------------------|------------------|
| creator-001 | 5 | ~0.00 | ~1.00 | ~0.35 |
| creator-002 | 5 | ~0.25 | ~0.75 | ~0.45 |
| creator-004 | 5 | ~0.22 | ~0.78 | ~0.44 |

> Derived values **differ** from static numbers in `creators.json` — expected. Dashboard uses live aggregation, not legacy fixture scores.

---

## What worked well

1. **Rich `content` text** produces more realistic claim extraction and per-post cards than title+summary alone.
2. **Three personas** map cleanly to demo narratives: credible tech explainer, mixed political commentator, markets creator with hype vs education split.
3. **Transparency summary** and **claims needing attention** render for all three; weakest-claim notes stay claim-focused, not personal attacks.
4. **Contrast is demo-ready:** DataDave shows more **low corroboration** patterns; Marcus shows intent-attribution examples; Nova mixes strong explainers with speculative AI labor claims.
5. **Internal demo form** (`/creators/demo`) plus fixtures give two paths to add transcripts before a meeting.
6. **Phase 3.8 docs** (`CREATOR_DEMO_SCRIPT.md`, outreach pack) align with what the UI actually shows.

---

## What felt confusing

1. **Metric drift:** Stakeholders may compare list cards to old `creators.json` numbers — need to say metrics are **derived at request time**.
2. **First load latency:** Initial `/creators` or detail visit analyzes many posts; no progress % beyond loading copy.
3. **High low corroboration after enrichment:** Fixture cross-source alignment is strict; dense new text can yield more **low corroboration** than the legacy static story — still valid for demos but requires explanation.
4. **creator-001 vs creator-003:** Docs often recommend Leila as the “strong” profile; after enrichment, Nova’s derived rates may look weaker — pick profiles by **live** dashboard, not JSON tables alone.
5. **Optional summary on demo form** merges into `content` — not stored as a separate field on posts.

---

## Source transparency clarity

| Question | Assessment |
|----------|------------|
| Does the dashboard explain **source transparency**? | **Mostly yes** — disclaimer, metric helpers, and “sample integrity profile” framing on list/detail. |
| Is **claim support** vs **low corroboration** distinguishable? | **Yes** — separate metrics and corroboration labels on post cards. |
| Is it clear this is not a verdict on the creator? | **Yes** — disclaimer and list intro state patterns from analyzed text, not character judgment. |

**Improve later:** Short inline glossary on detail page linking metric names to one example claim.

---

## Claim wording review

| Area | Finding |
|------|---------|
| UI labels | Uses **contradiction signals**, **low corroboration**, **framing indicators** — appropriate. |
| Weakest-claim notes | Generally neutral (“speculative prediction”, “intent attribution lacks cited evidence”). |
| Fixture post titles | DataDave titles use provocative phrasing (“lying”, “guaranteed”) — intentional for demo contrast; **spoken content** clarifies uncertainty where needed. |
| Transparency summaries | Auto-generated text is measured; no “bad creator” language observed. |

**Recommendation:** In live demos, open **claims needing attention** and read the **note** field, not only the post title.

---

## Improve later (not Phase 3.10)

- Live or richer corroboration sources (beyond fixtures)
- Progress indicator for multi-post analysis
- Sync or remove legacy metric fields in `creators.json` to avoid confusion
- Optional `summary` field on demo POST API stored separately from `content`
- Export transparency summary (PDF/static) for creator pilots
- In-app diff when a demo post is updated via `/creators/demo`

---

## Ready for controlled demos?

**Yes — with caveats.**

The creator dashboard is **ready for controlled demos** when you:

1. Use **creator-002 + creator-004** (or **creator-003 + creator-004**) for contrast.
2. Explain **fixture corroboration** and **derived metrics**.
3. Warm caches by opening profiles once before a live session (or run backend locally beforehand).
4. Use `/creators/demo` to add one fresh transcript if needed.

**Not ready for:** public launch, creator self-service onboarding, or unsupervised interpretation as a reputation score.

---

## How to re-run validation

```bash
cd backend
python3 scripts/enrich_demo_validation_content.py   # idempotent content merge
source .venv/bin/activate
pytest -q

# Smoke API
curl -s http://localhost:8000/v1/creators/creator-001 | python3 -m json.tool | head -40
```

Frontend (optional smoke):

```bash
cd frontend && npm run dev
# Open http://localhost:3000/creators/creator-001
#      http://localhost:3000/creators/creator-002
#      http://localhost:3000/creators/creator-004
```

---

*Phase 3.10 — validation and fixture enrichment only.*
