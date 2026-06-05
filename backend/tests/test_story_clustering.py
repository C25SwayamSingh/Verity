"""Story clustering + corroboration engine tests."""

from typing import List, Optional

from app.services.story_cluster_service import StoryClusterService


def _article(
    article_id: str,
    headline: str,
    source: str,
    published_at: str,
    *,
    summary: str = "",
    category: str = "breaking",
    key_claims: Optional[List[str]] = None,
    contradiction_warnings: Optional[List[str]] = None,
    credibility: float = 0.8,
) -> dict:
    return {
        "id": article_id,
        "headline": headline,
        "source": source,
        "category": category,
        "published_at": published_at,
        "neutral_summary": summary or headline,
        "importance_score": 0.8,
        "credibility_score": credibility,
        "relevance_score": 0.85,
        "freshness_score": 0.8,
        "source_diversity_score": 0.6,
        "framing_label": "mostly_neutral",
        "key_claims": key_claims or [],
        "support_summary": "",
        "contradiction_warnings": contradiction_warnings or [],
        "why_selected": "",
        "provider_name": "fixtures",
    }


def test_similar_articles_cluster_together():
    service = StoryClusterService()
    articles = [
        _article(
            "a1",
            "Central bank holds rates amid inflation concerns",
            "Reuters",
            "2026-06-04T12:00:00Z",
            key_claims=["Central bank held interest rates"],
        ),
        _article(
            "a2",
            "Fed keeps interest rates unchanged amid inflation",
            "AP",
            "2026-06-04T13:00:00Z",
            key_claims=["Central bank held interest rates"],
        ),
        _article(
            "a3",
            "Policymakers leave rates steady as inflation cools",
            "BBC News",
            "2026-06-04T14:00:00Z",
            key_claims=["Central bank held interest rates"],
        ),
    ]
    clusters = service.cluster_articles("breaking", articles)
    assert len(clusters) == 1
    cluster = clusters[0]
    assert cluster.source_count == 3
    assert cluster.independent_source_count == 3


def test_unrelated_articles_do_not_cluster_together():
    service = StoryClusterService()
    articles = [
        _article("a1", "Hurricane makes landfall in Florida", "Reuters", "2026-06-04T12:00:00Z"),
        _article("a2", "Tech company unveils new AI model", "TechCrunch", "2026-06-04T12:05:00Z"),
    ]
    clusters = service.cluster_articles("breaking", articles)
    assert len(clusters) == 2


def test_source_count_and_independent_source_count_handle_duplicates():
    service = StoryClusterService()
    articles = [
        _article(
            "a1",
            "Market volatility rises after CPI data",
            "Reuters",
            "2026-06-04T10:00:00Z",
            key_claims=["CPI data increased market volatility"],
        ),
        _article(
            "a2",
            "Stocks swing after CPI inflation print",
            "Reuters",
            "2026-06-04T10:20:00Z",
            key_claims=["CPI data increased market volatility"],
        ),
        _article(
            "a3",
            "Markets react to CPI report",
            "BBC News",
            "2026-06-04T10:40:00Z",
            key_claims=["CPI data increased market volatility"],
        ),
    ]
    clusters = service.cluster_articles("breaking", articles)
    cluster = clusters[0]
    assert cluster.source_count == 3
    assert cluster.independent_source_count == 2


def test_corroboration_signal_changes_with_source_agreement():
    service = StoryClusterService()
    high_overlap = [
        _article(
            "a1",
            "Central bank holds rates amid inflation concerns",
            "Reuters",
            "2026-06-04T12:00:00Z",
            key_claims=["Central bank held rates", "Inflation remained elevated"],
        ),
        _article(
            "a2",
            "Fed keeps rates steady amid inflation concerns",
            "AP",
            "2026-06-04T12:20:00Z",
            key_claims=["Central bank held rates", "Inflation remained elevated"],
        ),
        _article(
            "a3",
            "Officials keep rates unchanged as inflation cools slowly",
            "BBC News",
            "2026-06-04T12:40:00Z",
            key_claims=["Central bank held rates", "Inflation remained elevated"],
        ),
    ]
    low_overlap = [
        _article("b1", "Regional flood warning expanded", "Reuters", "2026-06-04T10:00:00Z"),
        _article("b2", "Parliament delays budget vote", "AP", "2026-06-04T10:30:00Z"),
    ]
    cluster_a = service.cluster_articles("breaking", high_overlap)[0]
    cluster_b = service.cluster_articles("breaking", low_overlap)[0]
    assert cluster_a.corroboration_signal["strength"] >= cluster_b.corroboration_signal["strength"]


def test_single_source_story_marked_single_source_or_limited():
    service = StoryClusterService()
    cluster = service.cluster_articles(
        "breaking",
        [_article("a1", "Single outlet reports policy shakeup", "Reuters", "2026-06-04T09:00:00Z")],
    )[0]
    assert cluster.corroboration_signal["level"] in {"single_source", "limited"}


def test_contradiction_warnings_are_conservative():
    service = StoryClusterService()
    clean_cluster = service.cluster_articles(
        "breaking",
        [
            _article(
                "a1",
                "Earthquake reported offshore",
                "Reuters",
                "2026-06-04T08:00:00Z",
                key_claims=["Offshore earthquake triggered alerts"],
            ),
            _article(
                "a2",
                "Offshore quake triggers alerts",
                "AP",
                "2026-06-04T08:20:00Z",
                key_claims=["Offshore earthquake triggered alerts"],
            ),
        ],
    )[0]
    assert clean_cluster.contradiction_warnings == []
    assert clean_cluster.differing_details == []

    warned_cluster = service.cluster_articles(
        "breaking",
        [
            _article(
                "b1",
                "Officials report quake toll",
                "Reuters",
                "2026-06-04T08:00:00Z",
                    key_claims=["Officials reported an initial casualty count"],
                contradiction_warnings=["Sources differ on casualty count."],
            ),
                _article(
                    "b2",
                    "Aftershock risk remains after quake",
                    "AP",
                    "2026-06-04T08:10:00Z",
                    key_claims=["Officials reported an initial casualty count"],
                ),
        ],
    )[0]
    assert warned_cluster.contradiction_warnings
    assert warned_cluster.differing_details
