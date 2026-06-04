"""Transcription provider interface — swappable (mock, OpenAI Whisper, etc.)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


class TranscriptionError(Exception):
    """Raised when audio cannot be transcribed."""


@dataclass
class TranscriptionResult:
    text: str
    provider: str
    language: str = "en"


class TranscriptionProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_path: Path) -> TranscriptionResult:
        """Transcribe audio at ``audio_path`` (wav/mp3/m4a)."""
