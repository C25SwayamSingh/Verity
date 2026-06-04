import re
import uuid
from typing import Optional

from sqlmodel import Session

from app.core.ingestion import (
    IngestionClassification,
    classify_ingestion,
)
from app.db.models import AnalysisRecord
from app.schemas.domain import (
    AnalyzeResponse,
    EligibilityResult,
    FramingOverallLabel,
    FramingResult,
    IngestionInfo,
    SUPPORTED_NEWS_CATEGORIES,
    UserCategory,
)
from app.services.claim_service import ClaimService
from app.services.framing_service import FramingService
from app.services.openai_client import OpenAIService
from app.services.rewrite_service import RewriteService
from app.services.sentence_service import SentenceService
from app.services.source_alignment_service import SourceAlignmentService

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "breaking": ["breaking", "just in", "developing", "urgent"],
    "domestic_us": [
        "congress",
        "white house",
        "federal",
        "u.s.",
        "united states",
        "senate",
        "supreme court",
        "washington",
    ],
    "foreign_world": [
        "europe",
        "nato",
        "ukraine",
        "china",
        "middle east",
        "united nations",
        "global",
    ],
    "markets_stocks": [
        "stock",
        "market",
        "nasdaq",
        "s&p",
        "earnings",
        "investors",
        "fed",
        "inflation",
        "unemployment",
    ],
    "tech_ai": [
        "artificial intelligence",
        " ai ",
        "openai",
        "machine learning",
        "startup",
        "software",
        "chip",
    ],
}

NON_NEWS_KEYWORDS = [
    "recipe",
    "ingredients",
    "preheat oven",
    "tablespoon",
    "cup of flour",
    "cooking tutorial",
    "skincare routine",
    "workout plan",
    "minecraft",
    "gameplay",
]


class IngestService:
    def __init__(self) -> None:
        self._openai = OpenAIService()
        self._sentences = SentenceService()
        self._claims = ClaimService(self._openai)
        self._alignment = SourceAlignmentService()
        self._framing = FramingService(self._openai)
        self._rewrite = RewriteService(self._openai)

    def run_analysis(
        self,
        text: str,
        content_type: str,
        user_selected_category: str,
    ) -> AnalyzeResponse:
        """Run the analysis pipeline without persisting to the database.

        For raw checker submissions the text is first classified. A link-only
        social/video (or other) URL is never treated as analyzable content;
        instead a clear "transcript or upload required" state is returned.
        """
        # Transcripts (e.g. from uploaded media) are already analyzable text.
        if content_type == "transcript":
            return self._analyze_text(text, user_selected_category, ingestion=None)

        classification = classify_ingestion(text)
        if classification.needs_more_input:
            return self._build_needs_more_input_response(classification)

        ingestion = IngestionInfo(
            ingestion_type=classification.ingestion_type,
            analyzable=True,
            needs_more_input=False,
            source_links=classification.source_links,
        )
        return self._analyze_text(
            classification.analyzable_text or text,
            user_selected_category,
            ingestion=ingestion,
        )

    def _analyze_text(
        self,
        text: str,
        user_selected_category: str,
        ingestion: Optional[IngestionInfo],
    ) -> AnalyzeResponse:
        cleaned, sentences = self._sentences.process(text)
        detected = self._detect_category(cleaned, user_selected_category)
        eligible = self._is_bias_framing_eligible(detected, cleaned, user_selected_category)
        eligibility = self._build_eligibility(detected, eligible, user_selected_category)

        summary, takeaways, notes = self._summarize(cleaned, eligible)

        raw_claims = self._claims.extract(sentences, cleaned)
        category_for_alignment = detected if eligible else user_selected_category
        claim_results = self._alignment.align_claims(raw_claims, category_for_alignment, eligible)

        framing = self._framing.analyze(cleaned, eligible)

        # Neutral / clearer rewrite is available for any content with enough
        # analyzable text — only full news bias/framing is gated by eligibility.
        rewrite_allowed = len(cleaned.strip()) >= 40
        neutral = self._rewrite.neutral_rewrite(cleaned, allow=rewrite_allowed)

        if ingestion and ingestion.source_links:
            notes.append(
                "Submitted link(s) kept as source metadata only — The Giver did not "
                "download, scrape, or transcribe linked content."
            )

        return AnalyzeResponse(
            analysis_id=str(uuid.uuid4()),
            summary=summary,
            key_takeaways=takeaways,
            claims=claim_results,
            framing=framing,
            neutral_rewrite=neutral,
            eligibility=eligibility,
            notes=notes,
            ingestion=ingestion,
        )

    def _build_needs_more_input_response(
        self, classification: IngestionClassification
    ) -> AnalyzeResponse:
        """Return a clear "transcript or upload required" state for link-only input."""
        summary = (
            "We found a link, but no transcript or analyzable text was provided, so "
            "The Giver did not analyze the link itself."
        )
        return AnalyzeResponse(
            analysis_id=str(uuid.uuid4()),
            summary=summary,
            key_takeaways=[],
            claims=[],
            framing=FramingResult(
                overall_label=FramingOverallLabel.mostly_neutral, indicators=[]
            ),
            neutral_rewrite="",
            eligibility=EligibilityResult(
                bias_framing_eligible=False,
                detected_category="unknown",
                reason=(
                    "No analyzable text was available. The Giver analyzes submitted or "
                    "generated text, not a raw link."
                ),
            ),
            notes=[classification.transparency_note] if classification.transparency_note else [],
            ingestion=IngestionInfo(
                ingestion_type=classification.ingestion_type,
                analyzable=False,
                needs_more_input=True,
                source_links=classification.source_links,
                guidance=classification.guidance,
                transparency_note=classification.transparency_note,
            ),
        )

    def analyze(
        self,
        text: str,
        content_type: str,
        user_selected_category: str,
        session: Session,
    ) -> AnalyzeResponse:
        response = self.run_analysis(text, content_type, user_selected_category)

        record = AnalysisRecord(
            id=response.analysis_id,
            request_text=text[:10000],
            content_type=content_type,
            user_selected_category=user_selected_category,
            result_json=response.model_dump_json(),
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        return response

    def get_by_id(self, analysis_id: str, session: Session) -> Optional[AnalyzeResponse]:
        record = session.get(AnalysisRecord, analysis_id)
        if not record:
            return None
        return AnalyzeResponse.model_validate_json(record.result_json)

    def _detect_category(self, text: str, user_selected: str) -> str:
        lower = f" {text.lower()} "
        for kw in NON_NEWS_KEYWORDS:
            if kw in lower:
                return UserCategory.other.value

        scores: dict[str, int] = {k: 0 for k in CATEGORY_KEYWORDS}
        for cat, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw in lower:
                    scores[cat] += 1

        best = max(scores, key=scores.get)
        if scores[best] == 0:
            try:
                UserCategory(user_selected)
                if user_selected != UserCategory.other.value:
                    return user_selected
            except ValueError:
                pass
            return UserCategory.other.value
        return best

    def _is_bias_framing_eligible(
        self, detected: str, text: str, user_selected: str
    ) -> bool:
        if detected == UserCategory.other.value:
            return False
        try:
            detected_enum = UserCategory(detected)
        except ValueError:
            return False
        if detected_enum not in SUPPORTED_NEWS_CATEGORIES:
            return False
        lower = text.lower()
        if any(kw in lower for kw in NON_NEWS_KEYWORDS):
            return False
        if len(text.strip()) < 80:
            return False
        return True

    def _build_eligibility(
        self, detected: str, eligible: bool, user_selected: str
    ) -> EligibilityResult:
        if eligible:
            return EligibilityResult(
                bias_framing_eligible=True,
                detected_category=detected,
                reason="Content appears to be news/current information within a supported category.",
            )
        if detected == UserCategory.other.value:
            reason = (
                "This content appears to be outside supported news/current-information categories. "
                "Summary and notes are available, but bias/framing analysis is not available."
            )
        elif user_selected != detected:
            reason = (
                f"Detected category '{detected}' differs from selection '{user_selected}'. "
                "Full framing and cross-source alignment require supported news content."
            )
        else:
            reason = "Content does not meet requirements for bias/framing and full corroboration analysis."
        return EligibilityResult(
            bias_framing_eligible=False,
            detected_category=detected,
            reason=reason,
        )

    def _summarize(self, text: str, eligible: bool) -> tuple[str, list[str], list[str]]:
        notes: list[str] = []
        if self._openai.available:
            payload = self._openai.complete_json(
                system=(
                    'Summarize news text for information integrity review. Return JSON: '
                    '{"summary":"2-3 sentences","key_takeaways":["..."],"notes":["optional"]}'
                ),
                user=text[:4000],
            )
            if payload:
                return (
                    str(payload.get("summary", "")),
                    list(payload.get("key_takeaways", []))[:5],
                    list(payload.get("notes", []))[:3],
                )

        sentences = re.split(r"(?<=[.!?])\s+", text)
        summary = " ".join(sentences[:2])[:500] if sentences else text[:500]
        takeaways = [s.strip() for s in sentences[:3] if len(s.strip()) > 20][:3]
        if not takeaways:
            takeaways = ["Submitted text was processed for claim and context signals."]
        if not eligible:
            notes.append(
                "Bias/framing and fixture-based corroboration were skipped based on content eligibility."
            )
        return summary, takeaways, notes
