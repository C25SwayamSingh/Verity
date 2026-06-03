import re
import uuid
from typing import Optional

from app.schemas.domain import ClaimType
from app.services.openai_client import OpenAIService

CLAIM_PATTERNS = [
    (r"\b(will|expected to|likely to|forecast)\b", ClaimType.prediction),
    (r"\b(should|must|need to|recommend)\b", ClaimType.advice),
    (r"\b(i think|in my view|believe|arguably)\b", ClaimType.opinion),
    (r"\b(best|#1|leading|exclusive offer)\b", ClaimType.promotional_claim),
    (r"\b(i saw|i experienced|my experience)\b", ClaimType.personal_experience),
]


class ClaimService:
    def __init__(self, openai: Optional[OpenAIService] = None) -> None:
        self._openai = openai or OpenAIService()

    def extract(self, sentences: list[str], full_text: str) -> list[dict]:
        llm_claims = self._extract_llm(sentences, full_text)
        if llm_claims:
            return llm_claims
        return self._extract_heuristic(sentences)

    def _extract_llm(self, sentences: list[str], full_text: str) -> list[dict]:
        if not self._openai.available:
            return []
        payload = self._openai.complete_json(
            system=(
                "Extract 3-8 distinct claims from news text. Return JSON: "
                '{"claims":[{"text":"...","claim_type":"factual_claim|opinion|advice|prediction|personal_experience|promotional_claim|unclear"}]}'
            ),
            user=f"Text:\n{full_text[:4000]}",
        )
        if not payload or "claims" not in payload:
            return []
        out = []
        for i, c in enumerate(payload["claims"][:8]):
            text = str(c.get("text", "")).strip()
            if len(text) < 10:
                continue
            ctype = self._normalize_type(str(c.get("claim_type", "unclear")))
            out.append({"claim_id": f"c{i+1}", "text": text, "claim_type": ctype})
        return out

    def _extract_heuristic(self, sentences: list[str]) -> list[dict]:
        candidates: list[dict] = []
        for sent in sentences:
            if not self._looks_like_claim(sent):
                continue
            ctype = self._classify_sentence(sent)
            candidates.append(
                {
                    "claim_id": f"c{len(candidates)+1}",
                    "text": sent[:400],
                    "claim_type": ctype,
                }
            )
            if len(candidates) >= 8:
                break
        if not candidates and sentences:
            candidates.append(
                {
                    "claim_id": "c1",
                    "text": sentences[0][:400],
                    "claim_type": ClaimType.unclear,
                }
            )
        return candidates

    def _looks_like_claim(self, sent: str) -> bool:
        if len(sent) < 25:
            return False
        if re.search(r"\b(report|said|according|data|percent|million|billion|announced)\b", sent, re.I):
            return True
        if re.search(r"\b(is|are|was|were|has|have)\b", sent, re.I) and len(sent.split()) >= 8:
            return True
        return False

    def _classify_sentence(self, sent: str) -> ClaimType:
        lower = sent.lower()
        for pattern, ctype in CLAIM_PATTERNS:
            if re.search(pattern, lower):
                return ctype
        if re.search(r"\b(according to|officials|department|study|survey)\b", lower):
            return ClaimType.factual_claim
        return ClaimType.factual_claim if len(sent) > 40 else ClaimType.unclear

    def _normalize_type(self, raw: str) -> ClaimType:
        try:
            return ClaimType(raw)
        except ValueError:
            return ClaimType.unclear

    def new_claim_id(self) -> str:
        return f"c-{uuid.uuid4().hex[:8]}"
