"""Central scoring definitions and derived integrity signals for The Giver's news product.

This module is the single source of truth for:

1. The composite ranking formula used by the Reliable News Dashboard and the
   News Integrity Feed (``SCORE_WEIGHTS`` + ``compute_final_score``).
2. Plain-English definitions of every score component (``SCORE_DEFINITIONS``),
   so the API can always explain what each number means.
3. Derived, non-weighted *signals* surfaced to users — cross-source
   corroboration, contradiction signals, framing indicators, source diversity,
   and an overall confidence signal.

IMPORTANT — language policy. The Giver does **not** compute a "truth score" or
decide whether a source is right or wrong. Every value here estimates how
*consistently* a story is reported and how *loaded* its language appears. Labels
use the approved vocabulary: source alignment, cross-source corroboration,
claim support, contradiction signals, framing indicators, source diversity,
confidence signal.
"""

from __future__ import annotations

from typing import Optional

# ---------------------------------------------------------------------------
# Composite ranking formula
# ---------------------------------------------------------------------------
#
# The weights are intentionally unchanged from the Phase 2 dashboard. The audit
# (see docs/SCORING_METHOD.md) concluded the weighting is justified for a *news
# discovery* ranking: importance and corroboration should dominate, freshness
# and diversity break ties. This is a ranking signal, not a verdict.

SCORE_WEIGHTS: dict[str, float] = {
    "importance_score": 0.35,
    "credibility_score": 0.30,
    "relevance_score": 0.20,
    "freshness_score": 0.10,
    "source_diversity_score": 0.05,
}

# Ordered, user-facing definitions of each component score. ``weighted`` marks
# whether the component contributes to ``final_score``.
SCORE_DEFINITIONS: list[dict] = [
    {
        "key": "importance_score",
        "label": "Importance",
        "weight": SCORE_WEIGHTS["importance_score"],
        "weighted": True,
        "description": (
            "Estimated significance of the story to the broader public — scale "
            "of impact, how many people are affected, and institutional weight. "
            "Does not judge whether the story is true."
        ),
    },
    {
        "key": "credibility_score",
        "label": "Credibility / corroboration",
        "weight": SCORE_WEIGHTS["credibility_score"],
        "weighted": True,
        "description": (
            "Cross-source corroboration strength: the track record of the "
            "reporting outlet(s) and how well independent sources report the "
            "same core facts. Higher means the central claims are echoed by more "
            "reliable, independent reporting — not that the story is verified true."
        ),
    },
    {
        "key": "relevance_score",
        "label": "Relevance",
        "weight": SCORE_WEIGHTS["relevance_score"],
        "weighted": True,
        "description": (
            "How closely the story matches the selected category and the current "
            "news cycle."
        ),
    },
    {
        "key": "freshness_score",
        "label": "Freshness",
        "weight": SCORE_WEIGHTS["freshness_score"],
        "weighted": True,
        "description": "Recency of the story relative to its publication time.",
    },
    {
        "key": "source_diversity_score",
        "label": "Source diversity",
        "weight": SCORE_WEIGHTS["source_diversity_score"],
        "weighted": True,
        "description": (
            "How many independent outlets cover the same story. Higher means "
            "broader, more independent coverage rather than a single origin."
        ),
    },
    {
        "key": "framing_signal_score",
        "label": "Framing indicator",
        "weight": 0.0,
        "weighted": False,
        "description": (
            "Whether the language appears loaded or one-sided. Surfaced as a "
            "signal only; it does not raise or lower the ranking score."
        ),
    },
    {
        "key": "contradiction_signal",
        "label": "Contradiction signal",
        "weight": 0.0,
        "weighted": False,
        "description": (
            "Whether independent sources disagree on key details. Surfaced as a "
            "caution signal only; it does not raise or lower the ranking score."
        ),
    },
]

SCORE_FORMULA = (
    "final_score = 0.35*importance + 0.30*credibility/corroboration "
    "+ 0.20*relevance + 0.10*freshness + 0.05*source_diversity"
)

SCORING_DISCLAIMER = (
    "These signals estimate how consistently a story is reported across sources "
    "and whether its language appears loaded. They are not a truth score and do "
    "not decide whether a source is right or wrong."
)


def compute_final_score(article: dict) -> float:
    """Composite ranking score in [0, 1], rounded to 4 dp.

    Missing component scores default to 0.0 so a partially-populated provider
    article never raises.
    """
    return round(
        sum(float(article.get(k, 0.0)) * w for k, w in SCORE_WEIGHTS.items()),
        4,
    )


# ---------------------------------------------------------------------------
# Framing label normalization
# ---------------------------------------------------------------------------

# Map any internal framing label to (level, user-facing text, 0-1 neutrality score).
_FRAMING_MAP: dict[str, tuple[str, str, float]] = {
    "mostly_neutral": ("neutral", "Mostly neutral language", 0.85),
    "mixed_framing": ("mixed", "Some framing language", 0.55),
    "notable_framing": ("notable", "Notable framing language", 0.25),
}


def framing_signal(article: dict) -> dict:
    """Framing indicator derived from the article's framing label."""
    label = (article.get("framing_label") or "mostly_neutral").strip()
    level, text, _score = _FRAMING_MAP.get(label, ("unknown", label.replace("_", " "), 0.5))
    return {"level": level, "label": text}


def framing_signal_score(article: dict) -> float:
    label = (article.get("framing_label") or "mostly_neutral").strip()
    return _FRAMING_MAP.get(label, ("", "", 0.5))[2]


# ---------------------------------------------------------------------------
# Cross-source corroboration / source alignment
# ---------------------------------------------------------------------------


def corroboration_signal(article: dict) -> dict:
    """Cross-source corroboration / source alignment signal.

    Combines source credibility (60%) and source diversity (40%) — i.e. how
    reliable the reporting is *and* how many independent outlets carry the same
    core facts. Returns a level, an approved-language label, and detail text.
    """
    credibility = float(article.get("credibility_score", 0.0))
    diversity = float(article.get("source_diversity_score", 0.0))
    strength = round(0.6 * credibility + 0.4 * diversity, 4)

    if strength >= 0.85:
        level, label = "strong", "Strong cross-source corroboration"
    elif strength >= 0.65:
        level, label = "moderate", "Moderate cross-source corroboration"
    elif strength >= 0.45:
        level, label = "limited", "Limited corroboration"
    else:
        level, label = "single_source", "Largely single-source so far"

    detail = (article.get("support_summary") or "").strip()
    return {"level": level, "label": label, "strength": strength, "detail": detail}


def contradiction_signal(article: dict) -> dict:
    """Whether independent sources disagree on key details."""
    warnings = [w for w in (article.get("contradiction_warnings") or []) if w]
    if warnings:
        return {
            "present": True,
            "label": "Contradiction signals present",
            "detail": "; ".join(warnings),
        }
    return {
        "present": False,
        "label": "No contradiction signals detected",
        "detail": "",
    }


def confidence_signal(article: dict) -> dict:
    """Overall confidence in the *integrity read* (not in the story being true).

    Blends the composite ranking with corroboration. A story with strong,
    diverse corroboration and no contradiction signals yields higher confidence
    that we are reading its cross-source picture well.
    """
    final = float(article.get("final_score") or compute_final_score(article))
    credibility = float(article.get("credibility_score", 0.0))
    diversity = float(article.get("source_diversity_score", 0.0))
    has_contradiction = bool([w for w in (article.get("contradiction_warnings") or []) if w])

    confidence = 0.5 * final + 0.3 * credibility + 0.2 * diversity
    if has_contradiction:
        confidence -= 0.15
    confidence = max(0.0, min(1.0, round(confidence, 4)))

    if confidence >= 0.8:
        level, label = "high", "High confidence signal"
    elif confidence >= 0.55:
        level, label = "medium", "Medium confidence signal"
    else:
        level, label = "low", "Low confidence signal"

    return {"level": level, "label": label, "score": confidence}


def why_selected(article: dict) -> str:
    """A short, plain-English 'why this story appears here' string.

    Falls back to a generated explanation when the provider did not supply one.
    """
    existing = (article.get("why_selected") or "").strip()
    if existing:
        return existing

    corr = corroboration_signal(article)
    fram = framing_signal(article)
    contra = contradiction_signal(article)
    bits = [
        f"{corr['label'].lower()}",
        f"{fram['label'].lower()}",
    ]
    if contra["present"]:
        bits.append("contradiction signals flagged for review")
    return "Surfaced for " + ", ".join(bits) + "."


def score_explanations() -> list[dict]:
    """Return the ordered, serializable list of score-component explanations."""
    return [dict(d) for d in SCORE_DEFINITIONS]
