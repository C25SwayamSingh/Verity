import re
from typing import Optional

from app.services.openai_client import OpenAIService


class RewriteService:
    def __init__(self, openai: Optional[OpenAIService] = None) -> None:
        self._openai = openai or OpenAIService()

    def neutral_rewrite(self, text: str, allow: bool = True) -> str:
        """Neutral / clearer rewrite of submitted text.

        Available for any content with enough analyzable text — not gated by
        news category. Only full news bias/framing analysis is category-gated.
        """
        if not allow:
            return (
                "A clearer rewrite was not generated because there was not enough "
                "analyzable text in the submission."
            )
        llm = self._rewrite_llm(text)
        if llm:
            return llm
        return self._rewrite_heuristic(text)

    def _rewrite_llm(self, text: str) -> Optional[str]:
        if not self._openai.available:
            return None
        payload = self._openai.complete_json(
            system='Rewrite the text in a neutral, clearer tone, preserving meaning. Return JSON: {"neutral_rewrite":"..."}',
            user=text[:4000],
        )
        if payload and payload.get("neutral_rewrite"):
            return str(payload["neutral_rewrite"]).strip()
        return None

    def _rewrite_heuristic(self, text: str) -> str:
        t = text
        replacements = [
            (r"\b(shocking|outrageous|terrible|amazing)\b", "", re.I),
            (r"\b(clearly|obviously|everyone knows)\b", "reportedly", re.I),
            (r"\b(worst|best) ever\b", "among recent records", re.I),
            (r"\s+", " ", 0),
        ]
        for pat, repl, flags in replacements:
            t = re.sub(pat, repl, t, flags=flags)
        t = t.strip()
        if len(t) > 600:
            t = t[:600] + "..."
        prefix = (
            "Neutral rewrite (heuristic): The following summarizes the submitted content "
            "using calmer, less loaded phrasing where possible. "
        )
        return prefix + t
