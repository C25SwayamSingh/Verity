# Demo Creator Profiles — Sample Integrity Profiles

Four fictional creators ship with The Giver. Metrics on `/creators` are **derived at runtime** from the analysis pipeline (`metrics_source: derived_from_analysis`), not the legacy numbers in `creators.json`. Use this guide to choose profiles for demos and outreach.

---

## Profile comparison (illustrative)

| ID | Name | Category | Demo role | Talking point |
|----|------|----------|-----------|----------------|
| `creator-001` | Nova Rivera | tech_ai | Balanced tech journalist | Strong citations; watch speculative AI labor claims |
| `creator-002` | Marcus Webb | domestic_us | Political commentator | Good primary docs; mixed **framing indicators** on intent |
| `creator-003` | Leila Okonkwo | foreign_world | High **source transparency** | Best “aspirational” profile for demos |
| `creator-004` | DataDave | markets_stocks | Cautionary contrast | More **low corroboration** and **contradiction signals** |

**Recommended contrast pair:** `creator-003` + `creator-004` (see `CREATOR_DEMO_SCRIPT.md`).

---

## creator-001 — Nova Rivera

- **Platform:** YouTube · **Handle:** @novarivera  
- **URL:** `/creators/creator-001`  
- **Use when:** Demoing tech/AI creators; audience cares about regulation and open source.

**Narrative:** Independent tech journalist with solid peer-reviewed and primary-document habits. **Claim support** is generally solid; **low corroboration** shows up on forward-looking employment claims. One post has a **contradiction signal** on an oversimplified open-source safety claim.

**Highlight on page:** Transparency summary (cites + labeled opinion); weakest claims on redundancy prediction.

**Sample line for outreach:** “Similar to channels that cite ArXiv and official texts but sometimes overstate timeline predictions.”

---

## creator-002 — Marcus Webb

- **Platform:** Twitter/X & Substack · **Handle:** @marcuswebb  
- **URL:** `/creators/creator-002`  
- **Use when:** Domestic policy, elections, institutional process.

**Narrative:** Former editor; strong on Congressional Record and Pew-style sources. **Framing indicators** trend mixed — intent attribution and coordination claims without **cross-source corroboration**.

**Highlight on page:** Contradiction vs. low corroboration on political intent claims; transparency summary on separating analysis from factual summary.

**Sample line for outreach:** “Shows how process-focused commentators can strengthen **source alignment** by sourcing intent claims the same way they source votes and bills.”

---

## creator-003 — Leila Okonkwo *(default “positive” demo)*

- **Platform:** Podcast & Substack · **Handle:** @leilaokonkwo  
- **URL:** `/creators/creator-003`  
- **Use when:** Default “strong **information integrity** habits” story for stakeholders.

**Narrative:** Think-tank-style sourcing (Foreign Affairs, ICG, UN reports). High **claim support** and **source diversity**. Single notable **contradiction signal** on an absolute sanctions claim — good example of “even strong creators get specific prompts.”

**Highlight on page:** Read transparency summary aloud; one weak claim as constructive feedback, not criticism.

**Sample line for outreach:** “This is what a **transparency summary** looks like when institutional sources dominate — with one claim flagged for qualification.”

---

## creator-004 — DataDave *(default “contrast” demo)*

- **Platform:** TikTok & YouTube · **Handle:** @realdatadave  
- **URL:** `/creators/creator-004`  
- **Use when:** Markets/retail investing; showing **low corroboration** without attacking personality.

**Narrative:** Uses real data names (Bloomberg, SEC) but often states predictions as certainties and attributes deception without sources. Higher **contradiction rate** and **low corroboration** — ideal for “what the dashboard surfaces” without saying “bad creator.”

**Highlight on page:** Claims needing attention (guaranteed returns, Fed “lying”); transparency summary on credentials disclosure.

**Sample line for outreach:** “Illustrates how **framing indicators** and thin **claim support** appear in finance content — useful for prep, not for public callouts.”

---

## Adding your own demo content

Fixture posts: `backend/app/providers/fixtures/creator_posts.json`  
Manual posts: `POST /v1/creators/{creator_id}/posts/demo` — see `CREATOR_DEMO_WORKFLOW.md`

Prefer attaching new transcripts to an existing fixture `creator_id` so the list/detail pages stay populated.

---

## IDs quick reference

```
creator-001  Nova Rivera      tech_ai
creator-002  Marcus Webb      domestic_us
creator-003  Leila Okonkwo    foreign_world
creator-004  DataDave         markets_stocks
```

---

*Phase 3.8 — documentation only.*
