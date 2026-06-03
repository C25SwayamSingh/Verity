from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.session import get_session, init_db
from app.middleware.rate_limit_middleware import AnalyzeRateLimitMiddleware
from app.schemas.api import AnalyzeRequest, AnalysisDetailResponse, HealthResponse
from app.schemas.dashboard import DashboardArticle, DashboardResponse
from app.services.dashboard_service import DashboardService, SUPPORTED_CATEGORIES
from app.services.ingest_service import IngestService

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="The Giver API",
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
_dashboard = DashboardService()


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


@app.get("/v1/analysis/{analysis_id}", response_model=AnalysisDetailResponse)
def get_analysis(analysis_id: str, session: Session = Depends(get_session)):
    result = _ingest.get_by_id(analysis_id, session)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result


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
