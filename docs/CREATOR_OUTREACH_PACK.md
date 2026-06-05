# Creator Outreach Pack — Verity (Phase 3.8)

Use this pack when reaching out to creators or briefing stakeholders. It complements the live demo script (`CREATOR_DEMO_SCRIPT.md`) and the technical workflow (`CREATOR_DEMO_WORKFLOW.md`).

---

## Quick links

| Resource | Purpose |
|----------|---------|
| [CREATOR_DEMO_SCRIPT.md](./CREATOR_DEMO_SCRIPT.md) | Step-by-step live demo (5–10 min) |
| [CREATOR_DEMO_WORKFLOW.md](./CREATOR_DEMO_WORKFLOW.md) | API + persistence for adding demo posts |
| [DEMO_CREATOR_PROFILES.md](./DEMO_CREATOR_PROFILES.md) | Sample integrity profiles and when to use each |
| `/creators` (local) | Creator list — sample integrity profiles |
| `/creators/creator-001` … `creator-004` | Detail pages — full transparency summary |

---

## What Verity measures

Verity produces **information integrity** reports for pasted articles, transcripts, or post text. For creators, it aggregates those reports into a **sample integrity profile** across analyzed posts.

| Signal | What it reflects |
|--------|------------------|
| **Claim support** | How often checkable claims show medium or high **cross-source corroboration** |
| **Source alignment** | How closely stated claims align with cited or cross-referenced sources |
| **Contradiction signals** | Claims where independent sources diverge from the statement |
| **Low corroboration** | Claims with limited supporting sources — areas where more sourcing may help |
| **Source diversity** | Breadth of independent publishers referenced |
| **Framing indicators** | Language patterns (e.g. certainty, blame, omission) — not a moral judgment |
| **Transparency summary** | Plain-language synthesis of sourcing habits and recurring patterns |

All of this is framed as **source transparency** and **claim support** — not a verdict on the creator or audience.

---

## What Verity does not measure

Be explicit in every conversation:

- It does **not** assign a “truth score” or label content as fake
- It does **not** prove a creator is right or wrong
- It does **not** replace editorial judgment, legal review, or platform policy
- It does **not** ingest live TikTok, Instagram, YouTube, X, or Substack feeds (demo uses fixtures + manual paste)
- It does **not** measure audience size, engagement, charisma, or entertainment value
- It does **not** offer a foolproof bias checker or public ranking for shaming

Corroboration in the current MVP uses **fixture-based cross-source alignment** for demos — not a live wire service. Say that clearly when asked about production readiness.

---

## Why creators would use it

Creators who explain news, policy, markets, or science often hear: *“Where did you get that?”* Verity helps answer that systematically.

1. **Audience trust** — Showing **source transparency** (what is corroborated, what needs more sourcing) signals respect for the audience’s ability to verify.
2. **Editorial hygiene** — Spot **low corroboration** and **contradiction signals** before publish, not only in the comments.
3. **Consistency** — A **transparency summary** across posts reveals habits: strong primary citations vs. opinion stated as fact.
4. **Differentiation** — Creators who already cite well can document **claim support** and **source alignment** as part of their brand — without claiming infallibility.
5. **Conversation, not condemnation** — Reports highlight *claims* and *sources*, not personal attacks.

Position Verity as a **transparency tool for the creator’s own workflow**, optional to share with audiences when they choose.

---

## How source transparency builds audience trust

Audiences increasingly distinguish *“I trust this person”* from *“I can check this claim.”* Verity bridges that gap:

- **Cross-source corroboration** shows when a claim lines up with reporting elsewhere — or when it stands alone.
- **Contradiction signals** flag when a strong statement conflicts with widely cited sources — a prompt to clarify, qualify, or add context.
- **Framing indicators** help creators see when tone may outrun evidence — without calling anyone dishonest.
- A **transparency summary** gives audiences a readable overview: sourcing strengths, recurring gaps, and how opinion is separated from factual summaries.

Trust grows when creators say: *“Here’s what we checked, here’s what’s well supported, here’s what we’re still verifying.”* That is **information integrity** as a practice, not a badge.

---

## Outreach message templates

Customize names and links. Keep tone curious and respectful — never accusatory.

### Template A — Short DM (cold or warm intro)

> Hi [Name] — I’m exploring tools that help information-focused creators show **source transparency** (claim support, cross-source corroboration, framing patterns) without labeling anyone “wrong.”
>
> We built a **sample integrity profile** demo — not connected to your live feed, just illustrative. Would you be open to a 10-minute walkthrough? No public listing, no scoring for shaming — just a transparency report you could use internally if useful.

### Template B — Email (slightly more context)

**Subject:** Optional transparency report for your sourcing workflow (demo)

> Hi [Name],
>
> I work on **Verity**, an information integrity platform that summarizes **source alignment**, **claim support**, **contradiction signals**, and **framing indicators** from text you choose to analyze (articles, transcripts, posts).
>
> It does **not** determine absolute truth or connect to your social accounts in the current demo. We use **sample integrity profiles** so creators can see the format before any real integration.
>
> If helpful, I’d love 10 minutes to show:
> - how **cross-source corroboration** and **low corroboration** appear per claim
> - how a **transparency summary** reads for audiences
> - what it explicitly does *not* measure
>
> Happy to use entirely fictional demo data or a transcript you paste yourself. Let me know if that’s interesting.
>
> Best,  
> [Your name]

### Template C — Follow-up after no reply

> Hi [Name] — quick bump in case the transparency demo got buried. Totally fine to pass. If you ever want a neutral second view on **source alignment** for a draft script (paste-only, private), I’m happy to run one post through the checker and share the report — no obligation to publish anything.

### Template D — After a positive demo

> Thanks again for the time today. As discussed, Verity is early — fixture-based corroboration for the demo, no live platform hookup yet. If you want to try your own transcript, the workflow is in our demo guide: paste via API or we can do it together. I’ll follow up when we have [in-app demo form / richer sourcing / whatever is true].

### What to avoid in outreach

- “Fake news detector,” “propaganda,” “bad creator,” “truth score”
- Implying you already analyzed *their* live channel without consent
- Public comparisons to other creators
- Promising legal compliance or platform safety certification

---

## Stakeholder demo narrative (3 minutes)

Use this arc before opening the UI. Full click-path: `CREATOR_DEMO_SCRIPT.md`.

1. **Problem (30s)** — Audiences want to verify claims; creators want trust without being reduced to a single score. News and commentary blur fact, prediction, and opinion.

2. **Approach (45s)** — Verity extracts claims, checks **cross-source corroboration** (demo: fixture alignment), surfaces **contradiction signals** and **framing indicators**, and writes a **transparency summary**. Language stays non-verdictive: **low corroboration**, not “false.”

3. **Two surfaces (45s)** — **Core Checker** (`/`) for one-off paste; **Creator dashboard** (`/creators`) for aggregated **sample integrity profiles** across posts.

4. **Live proof (60s)** — Open `creator-003` (strong sourcing) vs `creator-004` (more **low corroboration** and **contradiction signals**). Scroll **transparency summary** and “claims needing attention.” Read the on-page disclaimer aloud.

5. **Limits + roadmap (30s)** — No accounts, billing, or live social APIs yet; corroboration is demo fixtures; creators add posts via manual workflow. Next: in-app demo post form, optional opt-in sharing.

6. **Ask** — Pilot with 2–3 creators using paste-only transcripts; gather feedback on which metrics matter for their audience relationship.

---

## FAQ for creators (copy-paste friendly)

**Is this judging me?**  
No. It describes **claim support** and **source alignment** on text you submit. It’s a transparency aid, not a reputation score.

**Will my profile go public?**  
Not in the current product. Demo profiles are fictional samples unless you explicitly participate in a pilot.

**Can it read my YouTube channel automatically?**  
Not yet. You paste text or we use demo fixtures for illustrations.

**What should I do with low corroboration?**  
Often: add a source, soften certainty, or label as opinion/prediction. The report points to *claims*, not character.

---

## Checklist before outreach

- [ ] Backend and frontend running locally (or deployed demo URL)
- [ ] Reviewed `CREATOR_DEMO_SCRIPT.md` once
- [ ] Picked 2 sample profiles from `DEMO_CREATOR_PROFILES.md` (contrast pair)
- [ ] Disclaimer language practiced: measures alignment/support/framing; not absolute truth
- [ ] Confirmed you will **not** claim live analysis of their account without permission

---

*Phase 3.8 — documentation only. No product behavior changes.*
