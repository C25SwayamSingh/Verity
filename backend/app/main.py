from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.session import get_session, init_db
from app.middleware.rate_limit_middleware import AnalyzeRateLimitMiddleware
from app.schemas.api import AnalyzeRequest, AnalysisDetailResponse, HealthResponse
from app.schemas.creator import (
    CreateDemoCreatorPostRequest,
    CreateDemoCreatorPostResponse,
    CreatorListResponse,
    CreatorOverview,
    CreatorPostsResponse,
)
from app.schemas.dashboard import DashboardArticle, DashboardResponse
from app.schemas.news_feed import NewsFeedResponse, ScoringMethodResponse
from app.services.creator_service import CreatorService
from app.services.dashboard_service import DashboardService, SUPPORTED_CATEGORIES
from app.services.ingest_service import IngestService
from app.services.news_feed_service import NewsFeedService
from app.services.media_ingest_service import (
    MediaIngestService,
    MediaTooLargeError,
    UnsupportedMediaTypeError,
)
from app.services.transcription.base import TranscriptionError

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Verity API",
    description="Information integrity analysis — Phase 1 Core Checker MVP",
    version="0.1.0",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AnalyzeRateLimitMiddleware)

_ingest = IngestService()
_media = MediaIngestService(_ingest)
_dashboard = DashboardService()
_news_feed = NewsFeedService()
_creators = CreatorService()


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse()


@app.post("/v1/analyze", response_model=AnalysisDetailResponse)
def analyze(request: AnalyzeRequest, session: Session = Depends(get_session)):
    result = _ingest.analyze(
        text=request.text,
        content_type=request.content_type.value,
        user_selected_category=request.user_selected_category,
        session=session,
    )
    return result


@app.post("/v1/analyze/media", response_model=AnalysisDetailResponse)
async def analyze_media(
    session: Session = Depends(get_session),
    file: UploadFile = File(...),
    user_selected_category: str = Form("domestic_us"),
    media_kind: str = Form("video"),
    title: str = Form(""),
    source_url: str = Form(""),
):
    """
    Upload user-provided video/audio/screen recording → transcript → integrity analysis.
    Does not download or scrape social platform URLs.
    """
    if not file.filename:
        raise HTTPException(status_code=422, detail="Missing filename.")
    try:
        body = await file.read()
        return _media.analyze_upload(
            file_bytes=body,
            filename=file.filename,
            media_kind=media_kind,
            user_selected_category=user_selected_category,
            title=title,
            source_url=source_url,
            session=session,
        )
    except UnsupportedMediaTypeError as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc
    except MediaTooLargeError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    except TranscriptionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/v1/analysis/{analysis_id}", response_model=AnalysisDetailResponse)
def get_analysis(analysis_id: str, session: Session = Depends(get_session)):
    result = _ingest.get_by_id(analysis_id, session)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result


@app.get("/v1/news/feed", response_model=NewsFeedResponse)
def get_news_feed(category: str = "breaking"):
    """News Integrity Feed for the home page.

    Returns current stories for *category*, each annotated with cross-source
    corroboration, contradiction, framing, and confidence signals plus the score
    explanations. Provider failures fall back to fixtures automatically.
    """
    if category not in SUPPORTED_CATEGORIES:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported category '{category}'. Supported: {sorted(SUPPORTED_CATEGORIES)}",
        )
    return _news_feed.get_feed(category)


@app.get("/v1/news/scoring", response_model=ScoringMethodResponse)
def get_news_scoring():
    """Return the ranking formula, weights, and plain-English score definitions."""
    return _news_feed.scoring_method()


@app.get("/v1/dashboard/articles", response_model=DashboardResponse)
def get_dashboard_articles(category: str = "breaking"):
    if category not in SUPPORTED_CATEGORIES:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported category '{category}'. Supported: {sorted(SUPPORTED_CATEGORIES)}",
        )
    return _dashboard.get_top_articles(category)


@app.get("/v1/dashboard/articles/{article_id}", response_model=DashboardArticle)
def get_dashboard_article(article_id: str):
    result = _dashboard.get_article_by_id(article_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Article '{article_id}' not found.")
    return result


@app.get("/v1/creators", response_model=CreatorListResponse)
def list_creators(session: Session = Depends(get_session)):
    return _creators.list_creators(session)


@app.get("/v1/creators/{creator_id}", response_model=CreatorOverview)
def get_creator(creator_id: str, session: Session = Depends(get_session)):
    result = _creators.get_creator(session, creator_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Creator '{creator_id}' not found.")
    return result


@app.get("/v1/creators/{creator_id}/posts", response_model=CreatorPostsResponse)
def get_creator_posts(creator_id: str, session: Session = Depends(get_session)):
    result = _creators.get_creator_posts(session, creator_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Creator '{creator_id}' not found.")
    return result


@app.post(
    "/v1/creators/{creator_id}/posts/demo",
    response_model=CreateDemoCreatorPostResponse,
    status_code=201,
)
def add_demo_creator_post(
    creator_id: str,
    request: CreateDemoCreatorPostRequest,
    session: Session = Depends(get_session),
):
    """Add or update demo creator post content and run integrity analysis."""
    result = _creators.add_demo_post(session, creator_id, request)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Creator '{creator_id}' not found.")
    return result
