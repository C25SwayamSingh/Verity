from functools import lru_cache

from app.core.config import get_settings
from app.services.transcription.base import TranscriptionProvider
from app.services.transcription.mock_provider import MockTranscriptionProvider
from app.services.transcription.openai_whisper_provider import OpenAIWhisperTranscriptionProvider


@lru_cache
def get_transcription_provider() -> TranscriptionProvider:
    settings = get_settings()
    if settings.transcription_provider == "openai":
        return OpenAIWhisperTranscriptionProvider()
    return MockTranscriptionProvider()
