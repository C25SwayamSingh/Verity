# Scoring Method — The Giver News Integrity Feed & Dashboard

> Single source of truth in code: `backend/app/core/news_scoring.py`.

The Giver does **not** compute a "truth score" and does not decide whether a
source is right or wrong. Every number below estimates **how consistently a
story is reported across sources** and **whether its language appears loaded**.
It is a discovery/ranking signal plus transparency context — not a verdict.

## Composite ranking formula

```
final_score = 0.35 * importance_score
            + 0.30 * credibility_score      (a.k.a. corroboration)
            + 0.20 * relevance_score
            + 0.10 * freshness_score
            + 0.05 * source_diversity_score
```

All components are in `[0, 1]`; `final_score` is the weighted sum, rounded to 4
decimals. Weights are exposed at `GET /v1/news/scoring` and inside every
`GET /v1/news/feed` response (`score_explanations`).

### Audit decision

The Phase 2 weighting was reviewed and **kept** for this milestone. Rationale:

- **Importance (0.35)** and **corroboration (0.30)** should dominate a news
  discovery ranking — we want widely-significant, well-corroborated stories at
  the top.
- **Relevance (0.20)** keeps the category feed on-topic.
- **Freshness (0.10)** and **source diversity (0.05)** are tie-breakers; they
  matter but should not let a thin, single-source item outrank a major,
  well-corroborated story.

Changing the weights was not justified by evidence at this stage, so they remain
stable. If/when a real corroboration model lands (counting independent outlets
per story), revisit the importance vs. corroboration balance.

## Component definitions

| Component | Weighted? | What it estimates |
|---|---|---|
| `importance_score` | 35% | Significance to the broader public — scale of impact, number of people affected, institutional weight. Not a truth judgment. |
| `credibility_score` (corroboration) | 30% | Track record of the reporting outlet(s) **and** how well independent sources report the same core facts. Higher = central claims echoed by more reliable, independent reporting — not "verified true." |
| `relevance_score` | 20% | How closely the story matches the selected category and current news cycle. |
| `freshness_score` | 10% | Recency relative to publication time. |
| `source_diversity_score` | 5% | How many independent outlets cover the same story. Higher = broader, less single-origin coverage. |
| `framing_signal_score` | signal only | Whether language appears loaded/one-sided. Surfaced, not weighted into the rank. |
| `contradiction_signal` | signal only | Whether independent sources disagree on key details. Surfaced as a caution, not weighted. |

## Derived integrity signals (per feed item)

These are computed from the component scores and surfaced under each headline.
They do **not** change `final_score`.

- **Cross-source corroboration / source alignment** — `0.6*credibility +
  0.4*source_diversity`, mapped to: `strong` ≥ 0.85, `moderate` ≥ 0.65,
  `limited` ≥ 0.45, else `single_source`.
- **Contradiction signal** — `present: true` when the story carries
  contradiction warnings (independent sources disagree), else a neutral "no
  contradiction signals detected."
- **Framing indicator** — from the framing label: `mostly_neutral` → "Mostly
  neutral language", `mixed_framing` → "Some framing language", `notable_framing`
  → "Notable framing language."
- **Confidence signal** — confidence in the *integrity read* (not in the story
  being true): `0.5*final + 0.3*credibility + 0.2*source_diversity`, minus 0.15
  if contradiction signals are present. Mapped to `high` ≥ 0.8, `medium` ≥ 0.55,
  else `low`.
- **Why this story appears here** — provider-supplied rationale, or a generated
  one combining the corroboration + framing + contradiction signals.

## Language policy

Allowed: source alignment, cross-source corroboration, claim support,
contradiction signals, framing indicators, source diversity, confidence signal,
neutral rewrite, evidence-backed summary, most consistently reported details.

Avoided: truth score, fake news detector, propaganda detector, unbiased truth,
closest thing to truth, guaranteed accurate, proving a source right or wrong.

## Limitations

- Fixture and RSS/GDELT live data currently use **fixed defaults** for
  importance / relevance / source_diversity (and credibility from a domain prior
  for live sources). A real corroboration model — clustering the same story
  across independent outlets and counting agreement/disagreement — is future
  work. Until then, corroboration/diversity on live items is an estimate.
