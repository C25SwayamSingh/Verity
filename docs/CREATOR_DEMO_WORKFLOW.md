# Creator Demo Workflow

Use this guide to build and show **sample integrity profiles** on the Creator Integrity Dashboard—for demos, creator conversations, and stakeholder reviews—without live social media APIs.

**Phase 3.8 add-ons:** See the [Creator Outreach Pack](./CREATOR_OUTREACH_PACK.md) (creator-facing copy, outreach templates, stakeholder narrative), [Demo Script](./CREATOR_DEMO_SCRIPT.md) (live walkthrough), and [Demo Creator Profiles](./DEMO_CREATOR_PROFILES.md) (which fixture creator to show when).

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

## Add a demo post (API)

```bash
curl -X POST "http://localhost:8000/v1/creators/creator-001/posts/demo" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Fed holds rates steady — transcript excerpt",
    "content": "The Federal Reserve left interest rates unchanged on Wednesday, according to officials, as policymakers cited persistent inflation pressures. Stock indexes rose after several large companies reported earnings that exceeded expectations in the United States economy.",
    "topic": "monetary policy",
    "platform": "manual transcript",
    "content_type": "transcript"
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
| `creator_post_records` | Manually added demo posts |
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
- No in-app demo post form yet — use API/curl or preloaded fixtures (UI polish in Phase 3.7)
