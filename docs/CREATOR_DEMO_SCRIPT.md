# Creator Demo Script — Sample Integrity Dashboard

**Duration:** 8–10 minutes (5-minute version marked below)  
**Audience:** Creators, partners, or stakeholders  
**Prerequisites:** Backend on `:8000`, frontend on `:3000` — see `CREATOR_DEMO_WORKFLOW.md`

---

## Before you start

1. Open http://localhost:3000/creators in a clean browser window (zoom 100%, no unrelated tabs).
2. Skim `DEMO_CREATOR_PROFILES.md` — you will show **Leila Okonkwo** (`creator-003`) and **DataDave** (`creator-004`) for contrast.
3. Memorize one sentence: *“The Giver measures source alignment, claim support, and framing indicators. It does not determine absolute truth.”* (Also on every creator page.)

---

## Opening (60 seconds)

> “This is **The Giver** — an **information integrity** tool for people who explain news, policy, or technical topics. It’s not a fake-news label or a score that says someone is a bad creator. It helps show **source transparency**: which claims have **cross-source corroboration**, where we see **contradiction signals** or **low corroboration**, and how **framing indicators** show up across posts. What you’re looking at are **sample integrity profiles** — fictional creators with demo content, not live platform feeds.”

---

## Act 1 — Creator list (90 seconds)

**Navigate:** `/creators`

**Point out:**

- Intro copy: sample profiles, not a verdict on the creator
- Disclaimer banner (read it briefly)
- Metric cards: **source alignment**, **claim support**, **contradiction rate**, **low corroboration**, **source diversity**, **framing**
- Hover or expand **“what this means”** on one metric (e.g. claim support)

**Say:**

> “Each card is an aggregate over analyzed posts. Higher **claim support** means more checkable claims had medium or high corroboration in our demo source set. **Contradiction signals** are about the claim text, not attacking the person.”

**5-min cut:** Skip metric helpers; only show disclaimer + two names.

---

## Act 2 — Strong sample profile (2–3 minutes)

**Navigate:** `/creators/creator-003` (Leila Okonkwo — foreign_world)

**Walk top to bottom:**

1. **At-a-glance** — note relatively strong **source alignment** and **claim support**
2. **Transparency summary** — read one sentence aloud; emphasize institutional sources and neutral framing
3. **Claims needing attention** — open the sanctions claim example
   - Point to **contradiction signal** / contradicted corroboration status
   - Say: “This is a prompt to qualify or cite — not ‘Leila is wrong.’”
4. **Analyzed posts** — open one post; show per-claim corroboration labels
5. **Methodology** footer (if visible) — metrics derived from analysis pipeline, demo fixtures

**Say:**

> “This is what a creator with strong **source transparency** habits might see: mostly high corroboration, one **contradiction signal** to fix, and a **transparency summary** they could choose to share with their audience.”

---

## Act 3 — Contrast profile (2–3 minutes)

**Navigate:** `/creators/creator-004` (DataDave — markets_stocks)

**Emphasize differences:**

- Higher **low corroboration** and **contradiction** rates
- **Transparency summary** mentions certainty on predictions, institutional intent claims without sources
- **Claims needing attention** — price “guarantee,” Fed “lying” framing — always tie to *claims*, not character

**Say:**

> “Same system, different pattern. More areas where **claim support** is thin or **cross-source corroboration** diverges. A creator might use this in prep: add SEC filings, soften predictions, separate opinion from reported facts.”

**Do not say:** fake, propaganda, bad creator, truth score.

---

## Act 4 — Optional: Core Checker tie-in (90 seconds)

**Navigate:** `/`

Paste a short neutral paragraph (or use pre-copied Fed/rates example from `CREATOR_DEMO_WORKFLOW.md`).

> “The dashboard aggregates many runs of this pipeline. One paste → claims, corroboration, framing, neutral rewrite. Creators could run a single transcript before publish.”

**5-min cut:** Skip Act 4.

---

## Act 5 — Manual demo post (optional, technical audience)

Only if they ask “can I add my own text?”

Show curl or mention `POST /v1/creators/{id}/posts/demo` from `CREATOR_DEMO_WORKFLOW.md`.

> “You pick a fixture creator ID, paste a transcript, we persist the analysis and refresh the profile. Still no live TikTok or YouTube API.”

---

## Close (60 seconds)

> “Today this is a **demo pack**: sample profiles, fixture corroboration, paste-only workflow. What we’d love from you is whether **source transparency** reports would help your process — and which parts you’d ever show audiences vs. keep internal. We’re not building public shaming or proof that you’re right — we’re building clarity on **claim support** and **source alignment**.”

**Handoff:** `CREATOR_OUTREACH_PACK.md` (FAQ + email templates) if they want written follow-up.

---

## Demo paths (pick one)

| Path | Creators | Time | Best for |
|------|----------|------|----------|
| **Contrast** | `creator-003` + `creator-004` | 8 min | Default stakeholder/creator demo |
| **Tech creator** | `creator-001` only | 6 min | AI/tech journalists |
| **Policy commentator** | `creator-002` | 6 min | Domestic US, mixed framing |
| **Full tour** | All four on list | 12 min | Deep dive |

---

## Troubleshooting during live demo

| Issue | Fix |
|-------|-----|
| Empty or error on `/creators` | Confirm `NEXT_PUBLIC_API_URL`; restart backend |
| Metrics all zero | First request may analyze posts — wait, retry |
| “Wrong” numbers vs. JSON fixtures | Expected: runtime metrics are **derived_from_analysis**, not static JSON |
| Skeptic about sources | State clearly: demo uses fixture cross-source alignment, not live news APIs |

---

## Language cheat sheet

| Use | Avoid |
|-----|--------|
| source transparency | truth score |
| claim support | fake news detector |
| source alignment | propaganda detector |
| information integrity | bad creator |
| cross-source corroboration | proving someone is right |
| contradiction signals | foolproof bias checker |
| low corroboration | public shaming |
| framing indicators | |
| transparency summary | |
| sample integrity profile | |

---

*See also: `CREATOR_OUTREACH_PACK.md`, `CREATOR_DEMO_WORKFLOW.md`, `DEMO_CREATOR_PROFILES.md`*
