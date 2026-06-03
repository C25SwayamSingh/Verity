import json
import logging
from typing import Any, Optional

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.openai_api_key.strip()
        self._model = settings.openai_model
        self._client = None
        if self._api_key:
            try:
                from openai import OpenAI

                self._client = OpenAI(api_key=self._api_key)
            except Exception as e:
                logger.warning("OpenAI client init failed: %s", e)

    @property
    def available(self) -> bool:
        return self._client is not None

    def complete_json(self, system: str, user: str) -> Optional[dict[str, Any]]:
        if not self.available:
            return None
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            content = response.choices[0].message.content or "{}"
            return json.loads(content)
        except Exception as e:
            logger.warning("OpenAI request failed, using fallback: %s", e)
            return None
