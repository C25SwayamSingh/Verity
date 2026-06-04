"""OpenAI audio transcription when API key is configured."""

from pathlib import Path

from app.core.config import get_settings
from app.services.openai_client import OpenAIService
from app.services.transcription.base import TranscriptionError, TranscriptionProvider, TranscriptionResult
from app.services.transcription.mock_provider import MockTranscriptionProvider


class OpenAIWhisperTranscriptionProvider(TranscriptionProvider):
    def __init__(self) -> None:
        self._openai = OpenAIService()
        self._fallback = MockTranscriptionProvider()

    def transcribe(self, audio_path: Path) -> TranscriptionResult:
        if not self._openai.available:
            result = self._fallback.transcribe(audio_path)
            return TranscriptionResult(
                text=result.text,
                provider="mock_fallback_no_api_key",
                language=result.language,
            )

        try:
            from openai import OpenAI

            client = OpenAI(api_key=get_settings().openai_api_key)
            with audio_path.open("rb") as f:
                resp = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                )
            text = (resp.text or "").strip()
            if len(text) < 80:
                raise TranscriptionError(
                    "Transcription was too short to analyze. Try a longer clip or paste text directly."
                )
            return TranscriptionResult(text=text, provider="openai_whisper")
        except TranscriptionError:
            raise
        except Exception as exc:
            raise TranscriptionError(f"Transcription failed: {exc}") from exc
