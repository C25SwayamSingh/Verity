"""Deterministic transcription for tests and local dev without API keys."""

from pathlib import Path

from app.services.transcription.base import TranscriptionProvider, TranscriptionResult

# Information-dense sample text (≥80 chars) for checker eligibility in tests.
MOCK_TRANSCRIPT = (
    "The Federal Reserve left interest rates unchanged on Wednesday, according to officials, "
    "as policymakers cited persistent inflation pressures in the United States economy. "
    "Stock indexes rose after several large companies reported earnings that exceeded "
    "expectations, according to financial reporters and market analysts covering domestic "
    "economic policy and investor reaction."
)


class MockTranscriptionProvider(TranscriptionProvider):
    """Returns a fixed news-style transcript; ignores audio bytes."""

    def transcribe(self, audio_path: Path) -> TranscriptionResult:
        sidecar = audio_path.with_suffix(".txt")
        if sidecar.is_file():
            text = sidecar.read_text(encoding="utf-8").strip()
            if len(text) >= 80:
                return TranscriptionResult(text=text, provider="mock_sidecar")
        return TranscriptionResult(text=MOCK_TRANSCRIPT, provider="mock")
