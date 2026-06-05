"""Story clustering and evidence-backed corroboration engine (v1).

This service groups related articles into story clusters and derives feed
signals from actual source overlap instead of per-article defaults.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from statistics import mean
from typing import Optional

from app.core import news_scoring

_STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "of",
    "in",
    "on",
    "for",
    "to",
    "with",
    "after",
    "amid",
    "into",
    "from",
    "by",
    "at",
    "as",
    "is",
    "are",
    "was",
    "were",
    "be",
    "it",
    "its",
    "this",
    "that",
    "over",
    "new",
    "latest",
    "says",
    "say",
    "report",
    "reports",
    "reported",
}

_TOKEN_RE = re.compile(r"[a-z0-9]+")

_PUBLISHER_GROUPS = {
    "reuters": "wire_reuters",
    "reuters business": "wire_reuters",
    "associated press": "wire_ap",
    "ap": "wire_ap",
    "ap news": "wire_ap",
    "bbc": "bbc",
    "bbc news": "bbc",
    "bbc world": "bbc",
    "npr": "npr",
    "techcrunch": "techcrunch",
}

_FRAMING_SEVERITY = {
    "mostly_neutral": 1,
    "mixed_framing": 2,
    "notable_framing": 3,
}


def _normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _tokenize(text: str) -> set[str]:
    tokens = set()
    for tok in _TOKEN_RE.findall((text or "").lower()):
        if len(tok) < 3 or tok in _STOPWORDS:
            continue
        tokens.add(tok)
    return tokens


def _parse_published(value: str) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        return datetime.now(timezone.utc)


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a.intersection(b))
    union = len(a.union(b))
    if union == 0:
        return 0.0
    return inter / union


def _canonical_publisher(name: str) -> str:
    normalized = _normalize_spaces(re.sub(r"[^a-z0-9 ]", " ", (name or "").lower()))
    return _PUBLISHER_GROUPS.get(normalized, normalized or "unknown_source")


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


@dataclass
class PreparedArticle:
    raw: dict
    headline_tokens: set[str]
    detail_tokens: set[str]
    source_group: str
    source_name: str
    published_dt: datetime


@dataclass
class StoryCluster:
    cluster_id: str
    category: str
    representative_headline: str
    representative_summary: str
    articles: list[dict]
    publishers: list[str]
    source_count: int
    independent_source_count: int
    earliest_published_at: str
    latest_published_at: str
    common_reported_details: list[str]
    differing_details: list[str]
    contradiction_warnings: list[str]
    corroboration_signal: dict
    source_diversity_signal: dict
    confidence_signal: dict
    framing_signal: dict
    score_explanations: list[dict]
    importance_score: float
    credibility_score: float
    relevance_score: float
    freshness_score: float
    source_diversity_score: float
    final_score: float
    representative_article_id: str
    why_selected: str


@dataclass
class _ClusterDraft:
    category: str
    members: list[PreparedArticle] = field(default_factory=list)
    detail_union: set[str] = field(default_factory=set)
    earliest_dt: Optional[datetime] = None
    latest_dt: Optional[datetime] = None

    def add(self, article: PreparedArticle) -> None:
        self.members.append(article)
        self.detail_union.update(article.detail_tokens)
        if self.earliest_dt is None or article.published_dt < self.earliest_dt:
            self.earliest_dt = article.published_dt
        if self.latest_dt is None or article.published_dt > self.latest_dt:
            self.latest_dt = article.published_dt


class StoryClusterService:
    """Cluster related stories and derive evidence-backed feed signals."""

    def __init__(
        self,
        time_window_hours: int = 72,
        min_headline_similarity: float = 0.32,
        min_detail_similarity: float = 0.18,
    ) -> None:
        self._time_window_hours = time_window_hours
        self._min_headline_similarity = min_headline_similarity
        self._min_detail_similarity = min_detail_similarity

    def cluster_articles(self, category: str, articles: list[dict]) -> list[StoryCluster]:
        prepared = [self._prepare_article(a) for a in articles if a.get("category") == category]
        prepared.sort(key=lambda a: a.published_dt, reverse=True)

        drafts: list[_ClusterDraft] = []
        for article in prepared:
            best_idx = -1
            best_score = 0.0
            for idx, draft in enumerate(drafts):
                score = self._cluster_match_score(article, draft)
                if score > best_score:
                    best_score = score
                    best_idx = idx

            if best_idx >= 0:
                drafts[best_idx].add(article)
            else:
                draft = _ClusterDraft(category=category)
                draft.add(article)
                drafts.append(draft)

        clusters = [self._build_cluster(d) for d in drafts]
        clusters.sort(key=lambda c: c.final_score, reverse=True)
        return clusters

    # ------------------------------------------------------------------
    # Preparation / matching
    # ------------------------------------------------------------------

    def _prepare_article(self, article: dict) -> PreparedArticle:
        headline = article.get("headline", "")
        summary = article.get("neutral_summary", "")
        claims = article.get("key_claims", []) or []
        detail_text = " ".join([headline, summary] + claims)
        return PreparedArticle(
            raw=article,
            headline_tokens=_tokenize(headline),
            detail_tokens=_tokenize(detail_text),
            source_group=_canonical_publisher(article.get("source", "")),
            source_name=article.get("source", "Unknown"),
            published_dt=_parse_published(article.get("published_at", "")),
        )

    def _cluster_match_score(self, article: PreparedArticle, draft: _ClusterDraft) -> float:
        if draft.latest_dt is None:
            return 0.0
        delta_hours = abs((article.published_dt - draft.latest_dt).total_seconds()) / 3600
        if delta_hours > self._time_window_hours:
            return 0.0

        headline_similarity = max(
            (_jaccard(article.headline_tokens, m.headline_tokens) for m in draft.members),
            default=0.0,
        )
        detail_similarity = _jaccard(article.detail_tokens, draft.detail_union)
        keyword_overlap = 0.0
        if article.detail_tokens and draft.detail_union:
            keyword_overlap = len(article.detail_tokens & draft.detail_union) / max(
                1, min(len(article.detail_tokens), len(draft.detail_union))
            )

        if (
            headline_similarity < self._min_headline_similarity
            and detail_similarity < self._min_detail_similarity
        ):
            return 0.0

        return 0.55 * headline_similarity + 0.35 * detail_similarity + 0.10 * keyword_overlap

    # ------------------------------------------------------------------
    # Cluster synthesis
    # ------------------------------------------------------------------

    def _build_cluster(self, draft: _ClusterDraft) -> StoryCluster:
        members = draft.members
        members_sorted = sorted(
            members,
            key=lambda m: (
                float(m.raw.get("importance_score", 0.0)),
                m.published_dt,
            ),
            reverse=True,
        )
        representative = members_sorted[0]

        publishers = sorted({m.source_name for m in members})
        source_count = len(members)
        independent_groups = {m.source_group for m in members}
        independent_source_count = len(independent_groups)

        earliest_dt = min((m.published_dt for m in members), default=datetime.now(timezone.utc))
        latest_dt = max((m.published_dt for m in members), default=datetime.now(timezone.utc))
        overlap_score = self._source_overlap_score(members)

        contradiction_warnings = self._collect_warnings(members)
        common_details = self._common_reported_details(members)
        differing_details = list(contradiction_warnings)

        source_diversity_score = self._source_diversity_score(independent_source_count)
        avg_credibility = mean(float(m.raw.get("credibility_score", 0.0)) for m in members)
        credibility_score = _clamp(
            0.50 * overlap_score + 0.30 * source_diversity_score + 0.20 * avg_credibility
        )
        if independent_source_count <= 1:
            credibility_score = min(credibility_score, 0.38)

        importance_score = _clamp(
            mean(float(m.raw.get("importance_score", 0.0)) for m in members)
        )
        relevance_score = _clamp(mean(float(m.raw.get("relevance_score", 0.0)) for m in members))
        freshness_score = _clamp(
            max(float(m.raw.get("freshness_score", 0.0)) for m in members)
            - min(0.2, max(0.0, (latest_dt - earliest_dt).total_seconds() / 86400.0 * 0.02))
        )

        framing_label = self._framing_label(members)

        signal_seed = {
            "importance_score": importance_score,
            "credibility_score": credibility_score,
            "relevance_score": relevance_score,
            "freshness_score": freshness_score,
            "source_diversity_score": source_diversity_score,
            "framing_label": framing_label,
            "contradiction_warnings": contradiction_warnings,
            "support_summary": (
                f"Commonly reported by {independent_source_count} independent source "
                f"{'group' if independent_source_count == 1 else 'groups'}."
            ),
            "source_count": source_count,
            "independent_source_count": independent_source_count,
            "source_overlap_score": overlap_score,
        }
        final_score = news_scoring.compute_final_score(signal_seed)
        signal_seed["final_score"] = final_score

        corroboration = news_scoring.corroboration_signal(signal_seed)
        source_diversity_signal = news_scoring.source_diversity_signal(signal_seed)
        contradiction = news_scoring.contradiction_signal(signal_seed)
        framing = news_scoring.framing_signal(signal_seed)
        confidence = news_scoring.confidence_signal(signal_seed)

        cluster_id = self._cluster_id(draft.category, representative.raw.get("headline", ""), latest_dt)
        representative_article_id = representative.raw.get("id", cluster_id)
        why_selected = (
            f"Appears because {independent_source_count} independent sources report overlapping "
            f"details for this story cluster."
        )
        if contradiction["present"]:
            why_selected += " Some differing details are flagged for review."

        return StoryCluster(
            cluster_id=cluster_id,
            category=draft.category,
            representative_headline=representative.raw.get("headline", ""),
            representative_summary=representative.raw.get("neutral_summary", ""),
            articles=[
                {
                    "id": m.raw.get("id"),
                    "headline": m.raw.get("headline"),
                    "source": m.source_name,
                    "published_at": m.raw.get("published_at"),
                    "provider_name": m.raw.get("provider_name"),
                }
                for m in sorted(members, key=lambda mm: mm.published_dt, reverse=True)
            ],
            publishers=publishers,
            source_count=source_count,
            independent_source_count=independent_source_count,
            earliest_published_at=earliest_dt.isoformat(),
            latest_published_at=latest_dt.isoformat(),
            common_reported_details=common_details,
            differing_details=differing_details,
            contradiction_warnings=contradiction_warnings,
            corroboration_signal=corroboration,
            source_diversity_signal=source_diversity_signal,
            confidence_signal=confidence,
            framing_signal=framing,
            score_explanations=news_scoring.score_explanations(evidence_mode=True),
            importance_score=round(importance_score, 4),
            credibility_score=round(credibility_score, 4),
            relevance_score=round(relevance_score, 4),
            freshness_score=round(freshness_score, 4),
            source_diversity_score=round(source_diversity_score, 4),
            final_score=final_score,
            representative_article_id=representative_article_id,
            why_selected=why_selected,
        )

    def _source_overlap_score(self, members: list[PreparedArticle]) -> float:
        pairs: list[float] = []
        for idx, left in enumerate(members):
            for right in members[idx + 1 :]:
                if left.source_group == right.source_group:
                    continue
                pairs.append(_jaccard(left.detail_tokens, right.detail_tokens))
        if not pairs:
            return 0.0
        return round(mean(pairs), 4)

    def _source_diversity_score(self, independent_source_count: int) -> float:
        if independent_source_count <= 1:
            return 0.18
        if independent_source_count == 2:
            return 0.45
        if independent_source_count == 3:
            return 0.65
        if independent_source_count == 4:
            return 0.8
        return _clamp(0.8 + 0.05 * (independent_source_count - 4))

    def _collect_warnings(self, members: list[PreparedArticle]) -> list[str]:
        warnings: list[str] = []
        seen = set()
        for m in members:
            for warning in (m.raw.get("contradiction_warnings") or []):
                normalized = _normalize_spaces(str(warning))
                if not normalized:
                    continue
                key = normalized.lower()
                if key in seen:
                    continue
                seen.add(key)
                warnings.append(normalized)
        return warnings

    def _common_reported_details(self, members: list[PreparedArticle]) -> list[str]:
        claim_sources: dict[str, set[str]] = {}
        claim_display: dict[str, str] = {}
        for m in members:
            for claim in (m.raw.get("key_claims") or []):
                normalized = _normalize_spaces(str(claim))
                if not normalized:
                    continue
                key = normalized.lower()
                claim_sources.setdefault(key, set()).add(m.source_group)
                claim_display.setdefault(key, normalized)

        ranked_claims = sorted(
            (
                (len(groups), claim_display[key])
                for key, groups in claim_sources.items()
                if len(groups) >= 2
            ),
            reverse=True,
        )
        details = [claim for _, claim in ranked_claims[:5]]
        if details:
            return details

        token_sources: dict[str, set[str]] = {}
        for m in members:
            for token in m.headline_tokens:
                token_sources.setdefault(token, set()).add(m.source_group)

        fallback_tokens = [
            tok
            for tok, groups in sorted(
                token_sources.items(),
                key=lambda item: (len(item[1]), item[0]),
                reverse=True,
            )
            if len(groups) >= 2 and len(tok) >= 5
        ][:3]
        return [f"Multiple sources reference {tok} in their coverage." for tok in fallback_tokens]

    def _framing_label(self, members: list[PreparedArticle]) -> str:
        counts: dict[str, int] = {"mostly_neutral": 0, "mixed_framing": 0, "notable_framing": 0}
        for m in members:
            label = str(m.raw.get("framing_label") or "mostly_neutral")
            if label not in counts:
                continue
            counts[label] += 1
        ranked = sorted(
            counts.items(),
            key=lambda item: (item[1], _FRAMING_SEVERITY.get(item[0], 0)),
            reverse=True,
        )
        return ranked[0][0] if ranked else "mostly_neutral"

    def _cluster_id(self, category: str, headline: str, latest_dt: datetime) -> str:
        raw = f"{category}:{headline.lower()}:{latest_dt.date().isoformat()}"
        return "cluster_" + hashlib.md5(raw.encode()).hexdigest()[:12]

