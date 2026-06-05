# Creator Demo Workflow

Use this guide to build and show **sample integrity profiles** on the Creator Integrity Dashboard—for demos, creator conversations, and stakeholder reviews—without live social media APIs.

**Phase 3.8 add-ons:** See the [Creator Outreach Pack](./CREATOR_OUTREACH_PACK.md) (creator-facing copy, outreach templates, stakeholder narrative), [Demo Script](./CREATOR_DEMO_SCRIPT.md) (live walkthrough), and [Demo Creator Profiles](./DEMO_CREATOR_PROFILES.md) (which fixture creator to show when).

**Phase 3.10 validation:** See [CREATOR_DEMO_VALIDATION.md](./CREATOR_DEMO_VALIDATION.md) for enriched sample profiles (`creator-001`, `creator-002`, `creator-004`) and demo-readiness notes.

**Phase 4A media upload:** See [MEDIA_UPLOAD.md](./MEDIA_UPLOAD.md) — upload video/audio/screen recording on `/` for transcript → analysis. Instagram/TikTok links in the demo form remain **metadata only**; use screen recording upload or pasted source notes for Reels.

---

## Input basis (non-verbatim demos)

The internal form at `/creators/demo` requires an **input basis** so the dashboard does not imply Verity watched or transcribed the original video.

| Input basis | When to use |
|-------------|-------------|
| **Third-party extracted key points** (default) | Fofo-style bullets, manual notes from watching a Reel — **not** an official transcript |
| **Manual summary / source notes** | Your own write-up of what the post discussed |
| **Caption text** | Platform caption only |
| **Manual rough transcript** | Hand-typed, partial, or unverified transcript |
| **Full transcript** | Complete verbatim transcript you trust |

**Rules:**

- Analysis quality depends on the **submitted text** only.
- Non-verbatim posts show an amber note on the creator post card: analysis based on provided source notes, not a verbatim transcript.
- The checker still runs **claim support**, **cross-source corroboration**, **contradiction signals**, **framing indicators**, and **neutral rewrite** on whatever you paste.
- Do **not** label Fofo key points as “Full transcript.”

### Instagram Reel demos (Fofo-style key points)

Use fixture creator IDs (e.g. map `jayvolp` → `creator-004` for markets, or add posts under any fixture ID). Examples documented below — paste into **Provided source notes / text** with input basis **Third-party extracted key points**.

See [Sample Instagram demo inputs](#sample-instagram-demo-inputs) at the end of this file.

---

## What you need

- Backend running (`uvicorn app.main:app --reload --port 8000`)
- Frontend running (`npm run dev` in `frontend/`)
- A creator already defined in `backend/app/providers/fixtures/creators.json` (`creator-001` … `creator-004`)

---

## Recommended demo flow (first time)

1. Read the opening paragraph in [CREATOR_DEMO_SCRIPT.md](./CREATOR_DEMO_SCRIPT.md) (30 seconds).
2. Open http://localhost:3000/creators — confirm disclaimer and sample profile cards load.
3. Walk **creator-003** then **creator-004** for contrast (strong **source transparency** vs. more **low corroboration**).
4. Optionally add a live transcript via the demo API (below) and refresh the detail page.
5. Send follow-up using templates in [CREATOR_OUTREACH_PACK.md](./CREATOR_OUTREACH_PACK.md).

---

## Workflow overview

1. **Choose a creator** from the fixture list (see [DEMO_CREATOR_PROFILES.md](./DEMO_CREATOR_PROFILES.md)).
2. **Collect text** manually: paste a post, article excerpt, or video transcript (minimum 80 characters for full framing eligibility).
3. **Submit** via the demo API endpoint (below) or rely on fixture posts in `creator_posts.json` for static demos.
4. **Open** `/creators/{creator_id}` to view **source alignment**, **claim support**, **contradiction signals**, **framing indicators**, and the **transparency summary**.

Analyses are stored in SQLite (`creator_post_analysis_records`). Reopening the dashboard reuses cached results unless post content changes.

---

## Add a demo post (UI — recommended)

1. Open http://localhost:3000/creators/demo (or **Add demo creator post** from `/creators`).
2. Select a fixture **creator ID**, **input basis**, title, platform (e.g. Instagram), topic, original link, and provided source notes (≥80 characters).
3. Submit — the app calls `POST /v1/creators/{id}/posts/demo`, runs analysis, and persists to SQLite including `input_basis`.
4. Use **View sample integrity profile →** to open `/creators/{id}` with updated metrics.

Optional query param: `/creators/demo?creator_id=creator-003` pre-fills the creator.

## Add a demo post (API)

```bash
curl -X POST "http://localhost:8000/v1/creators/creator-001/posts/demo" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Fed holds rates steady — transcript excerpt",
    "content": "The Federal Reserve left interest rates unchanged on Wednesday, according to officials, as policymakers cited persistent inflation pressures. Stock indexes rose after several large companies reported earnings that exceeded expectations in the United States economy.",
    "topic": "monetary policy",
    "platform": "Instagram",
    "content_type": "pasted_text",
    "input_basis": "third_party_extracted_key_points"
  }'
```

Optional fields:

| Field | Notes |
|-------|--------|
| `post_id` | Custom ID; omit to auto-generate `demo-…` |
| `published_at` | ISO timestamp; defaults to now |
| `source_url` | Link to original post (optional) |
| `content_type` | `article`, `transcript`, or `pasted_text` |

Updating the same `post_id` with new `content` invalidates the cached analysis and triggers recomputation.

---

## View results

| Page | URL |
|------|-----|
| Creator list | http://localhost:3000/creators |
| Nova Rivera (tech) | http://localhost:3000/creators/creator-001 |
| Marcus Webb (domestic) | http://localhost:3000/creators/creator-002 |
| Leila Okonkwo (foreign) | http://localhost:3000/creators/creator-003 |
| DataDave (markets) | http://localhost:3000/creators/creator-004 |

---

## Fixture posts (bulk demos)

Existing posts live in `backend/app/providers/fixtures/creator_posts.json`. Each post can include a `content` field with full analyzable text; otherwise title + summary + claim lines are combined automatically.

Creator identity and bios: `backend/app/providers/fixtures/creators.json`.

---

## Persistence

| Table | Purpose |
|-------|---------|
| `creator_post_records` | Manually added demo posts (includes `input_basis`) |
| `creator_post_analysis_records` | Cached analysis JSON + content hash |

Content hash change detection ensures edits trigger a fresh integrity run.

---

## Product language

Describe outcomes as **source transparency**, **source alignment**, **claim support**, **cross-source corroboration**, **contradiction signals**, **low corroboration**, **framing indicators**, and **transparency summary** — not “truth scores,” “fake news,” or “bad creator.”

On-page disclaimer (also in UI): measures alignment, support, and framing; does **not** determine absolute truth.

---

## Documentation index (Phase 3.8)

| File | Contents |
|------|----------|
| [CREATOR_DEMO_WORKFLOW.md](./CREATOR_DEMO_WORKFLOW.md) | This file — technical workflow |
| [CREATOR_DEMO_SCRIPT.md](./CREATOR_DEMO_SCRIPT.md) | Live demo script |
| [CREATOR_OUTREACH_PACK.md](./CREATOR_OUTREACH_PACK.md) | Creator copy, outreach templates, stakeholder narrative |
| [DEMO_CREATOR_PROFILES.md](./DEMO_CREATOR_PROFILES.md) | When to use each sample profile |

---

## Limitations

- No TikTok, Instagram, YouTube, or X ingestion
- No creator accounts, billing, or public badges
- Creator identity from fixtures; **posts** added via API merge with fixture posts
- Cross-source alignment in MVP uses **fixture corroboration**, not live news APIs
- Demo post form at `/creators/demo` is internal-only (no auth); not creator onboarding
- No automatic Instagram/TikTok transcription or video download — paste text only

---

## Sample Instagram demo inputs

Documented examples for real Reel testing (not hardcoded in fixtures). Use **Third-party extracted key points** unless you have a full transcript.

### Sample 1 — jayvolp / Anthropic IPO speculation

- **Title:** Anthropic IPO discussion and market speculation  
- **Platform:** Instagram  
- **Link:** https://www.instagram.com/reel/DZGIvpnyrTD/  
- **Source notes:** Discussion of speculation around a potential Anthropic IPO; described as one of the most closely watched technology IPOs in recent years; audience comments mention buzz on the Fomo app; some comments joke about buying puts; tied to public interest in AI company valuations and future public offerings.

### Sample 2 — brycent / Phia funding

- **Title:** Phia startup funding and AI shopping app discussion  
- **Platform:** Instagram  
- **Link:** https://www.instagram.com/reel/DZIzNuKS60u/  
- **Source notes:** Phia, an AI shopping app founded by Phoebe Gates and Sophia Kianni; reported $35.5M Series A; angel investors named including Khloe Kardashian, Sydney Sweeney, Alix Earle, Jessica Alba, Paris Hilton, Vlad Tenev, and Shaboozey; platform helps users find savings; emphasizes distribution and cultural visibility in startup investment.

### Sample 3 — 60 Minutes / oil trade

- **Title:** $800 million oil trade raises insider trading questions  
- **Platform:** Instagram  
- **Link:** https://www.instagram.com/reel/DYfZ4ODxqdD/  
- **Source notes:** $800M bet on oil falling at 6:50 a.m. March 23; fifteen minutes later President Trump announced productive Iran talks on Truth Social; oil prices reportedly dropped more than 10%; trade allegedly generated tens of millions in profit; David Kovel cited on insider trading as a natural suspicion — frame as question, not confirmed conclusion.

### Sample 4 — tradeshipuniversity / politics and markets

- **Title:** Trump, markets, and concerns about political influence on trades  
- **Platform:** Instagram  
- **Link:** https://www.instagram.com/reel/DXAOA0Wkj4I/  
- **Source notes:** Politics, markets, stocks, crypto, war-related financial uncertainty; caption frustration about politics and finance; comments mention market manipulation, extreme valuations, Palantir trading around 176× earnings; connects political events and public statements to market behavior.
