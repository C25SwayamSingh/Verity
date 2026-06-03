import re
from typing import Optional

from app.schemas.domain import (
    FramingIndicator,
    FramingIndicatorType,
    FramingOverallLabel,
    FramingResult,
)
from app.services.openai_client import OpenAIService

EMOTIONAL_WORDS = [
    "outrageous",
    "shocking",
    "disaster",
    "catastrophic",
    "amazing",
    "terrible",
    "horrific",
    "devastating",
    "unprecedented",
    "scandal",
]
EXAGGERATION = [r"\b(always|never|every single|completely|totally)\b", r"\b(worst|best) ever\b"]
ONE_SIDED = [r"\b(only|everyone knows|clearly|obviously)\b", r"\b(the real truth|what they won't tell you)\b"]


class FramingService:
    def __init__(self, openai: Optional[OpenAIService] = None) -> None:
        self._openai = openai or OpenAIService()

    def analyze(self, text: str, eligible: bool) -> FramingResult:
        if not eligible:
            return FramingResult(
                overall_label=FramingOverallLabel.mostly_neutral,
                indicators=[],
            )
        llm = self._analyze_llm(text)
        if llm:
            return llm
        return self._analyze_heuristic(text)

    def _analyze_heuristic(self, text: str) -> FramingResult:
        lower = text.lower()
        indicators: list[FramingIndicator] = []

        found_emotional = [w for w in EMOTIONAL_WORDS if w in lower]
        if found_emotional:
            indicators.append(
                FramingIndicator(
                    indicator_type=FramingIndicatorType.emotionally_loaded_language,
                    description="Language may amplify emotional response beyond neutral reporting.",
                    examples=found_emotional[:3],
                )
            )

        for pat in EXAGGERATION:
            if re.search(pat, lower):
                indicators.append(
                    FramingIndicator(
                        indicator_type=FramingIndicatorType.exaggerated_language,
                        description="Absolute or extreme wording may overstate certainty.",
                        examples=[pat],
                    )
                )
                break

        for pat in ONE_SIDED:
            if re.search(pat, lower):
                indicators.append(
                    FramingIndicator(
                        indicator_type=FramingIndicatorType.one_sided_framing,
                        description="Phrasing may present one perspective without balancing alternatives.",
                        examples=[],
                    )
                )
                break

        if re.search(r"\b(i think|clearly|obviously)\b", lower) and re.search(
            r"\b(report|data|official)\b", lower
        ):
            indicators.append(
                FramingIndicator(
                    indicator_type=FramingIndicatorType.opinion_presented_as_fact,
                    description="Subjective language appears near factual-sounding statements.",
                    examples=[],
                )
            )

        if len(text) < 200:
            indicators.append(
                FramingIndicator(
                    indicator_type=FramingIndicatorType.missing_context,
                    description="Short input may lack context needed for balanced interpretation.",
                    examples=[],
                )
            )

        label = FramingOverallLabel.mostly_neutral
        if len(indicators) >= 3:
            label = FramingOverallLabel.notable_framing
        elif len(indicators) >= 1:
            label = FramingOverallLabel.mixed_framing

        return FramingResult(overall_label=label, indicators=indicators)

    def _analyze_llm(self, text: str) -> Optional[FramingResult]:
        if not self._openai.available:
            return None
        payload = self._openai.complete_json(
            system=(
                'Analyze framing in news text. Return JSON: {"overall_label":"mostly_neutral|mixed_framing|notable_framing",'
                '"indicators":[{"indicator_type":"emotionally_loaded_language|one_sided_framing|opinion_presented_as_fact|missing_context|exaggerated_language","description":"...","examples":[]}]}'
            ),
            user=text[:3500],
        )
        if not payload:
            return None
        try:
            label = FramingOverallLabel(payload.get("overall_label", "mostly_neutral"))
        except ValueError:
            label = FramingOverallLabel.mixed_framing
        indicators = []
        for ind in payload.get("indicators", [])[:5]:
            try:
                itype = FramingIndicatorType(ind["indicator_type"])
            except (KeyError, ValueError):
                continue
            indicators.append(
                FramingIndicator(
                    indicator_type=itype,
                    description=str(ind.get("description", "")),
                    examples=list(ind.get("examples", []))[:3],
                )
            )
        return FramingResult(overall_label=label, indicators=indicators)
