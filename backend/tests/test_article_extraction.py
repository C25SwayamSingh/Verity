"""Article URL → fetch + extract real text → checker pipeline (no network)."""

from app.services.article_extraction_service import (
    ArticleExtractionService,
    ExtractedArticle,
    FetchedPage,
)
from app.services.ingest_service import IngestService

ARTICLE_URL = "https://www.theguardian.com/us-news/2026/jun/04/senate-vote"
SOCIAL_URL = "https://www.instagram.com/reel/DXAOA0Wkj4I/"

ARTICLE_BODY = (
    "Senate Republicans narrowly blocked a bipartisan bid on Wednesday, according to officials, "
    "as lawmakers in Washington debated federal spending. The vote in the United States Senate "
    "fell largely along party lines. Supporters in Congress said the measure would fund key "
    "programs, while opponents argued it raised the deficit. The White House urged a renewed "
    "negotiation before the deadline at the end of the month."
)

SAMPLE_HTML = f"""
<html><head><title>Senate Republicans narrowly block bid | The Guardian</title></head>
<body>
  <nav>Menu Home News Opinion</nav>
  <article>
    <h1>Senate Republicans narrowly block bid</h1>
    <p>{ARTICLE_BODY}</p>
    <p>The debate is expected to continue next week, officials said.</p>
  </article>
  <footer>Copyright The Guardian</footer>
</body></html>
"""


class StubExtractor:
    """Stands in for ArticleExtractionService in IngestService wiring tests."""

    def __init__(self, result):
        self.result = result
        self.calls: list[str] = []

    def extract(self, url):
        self.calls.append(url)
        return self.result


def test_article_url_extracted_and_analyzed():
    stub = StubExtractor(
        ExtractedArticle(url=ARTICLE_URL, title="Senate blocks bid", text=ARTICLE_BODY)
    )
    ingest = IngestService(article_extractor=stub)
    r = ingest.run_analysis(ARTICLE_URL, "article", "domestic_us")

    assert stub.calls == [ARTICLE_URL]
    assert r.ingestion.needs_more_input is False
    assert r.ingestion.ingestion_type == "article_url"
    assert "extracted" in (r.ingestion.transparency_note or "").lower()
    assert r.summary
    assert ARTICLE_URL not in r.summary


def test_article_url_extraction_failure_falls_back_to_needs_more_input():
    ingest = IngestService(article_extractor=StubExtractor(None))
    r = ingest.run_analysis(ARTICLE_URL, "article", "domestic_us")
    assert r.ingestion.needs_more_input is True
    assert r.ingestion.ingestion_type == "article_url"


def test_social_video_url_never_calls_extractor():
    stub = StubExtractor(
        ExtractedArticle(url=SOCIAL_URL, title="x", text=ARTICLE_BODY)
    )
    ingest = IngestService(article_extractor=stub)
    r = ingest.run_analysis(SOCIAL_URL, "article", "domestic_us")
    assert stub.calls == []  # social links are never fetched
    assert r.ingestion.needs_more_input is True
    assert r.ingestion.ingestion_type == "social_video_url"


def test_extraction_service_parses_html_via_injected_fetcher():
    service = ArticleExtractionService(
        fetcher=lambda url: FetchedPage(url=url, html=SAMPLE_HTML)
    )
    article = service.extract(ARTICLE_URL)
    assert article is not None
    assert "Senate Republicans" in article.text
    assert "Copyright The Guardian" not in article.text  # boilerplate stripped


def test_extraction_service_returns_none_on_short_content():
    service = ArticleExtractionService(
        fetcher=lambda url: FetchedPage(url=url, html="<html><body><p>Too short.</p></body></html>")
    )
    assert service.extract(ARTICLE_URL) is None


def test_extraction_service_handles_fetch_exception():
    def boom(url):
        raise RuntimeError("network down")

    service = ArticleExtractionService(fetcher=boom)
    assert service.extract(ARTICLE_URL) is None
