"""Phase 4A — media upload → transcript → analysis."""

from io import BytesIO
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.media_ingest_service import MediaIngestService
from app.services.transcription.base import TranscriptionError, TranscriptionResult
from app.services.transcription.mock_provider import MOCK_TRANSCRIPT

client = TestClient(app)

SAMPLE_MP3 = b"\x00" * 1024


class FailingTranscriptionProvider:
    def transcribe(self, audio_path):
        raise TranscriptionError("Transcription service unavailable for test.")


class CustomTranscriptionProvider:
    def transcribe(self, audio_path):
        return TranscriptionResult(text=MOCK_TRANSCRIPT, provider="test_custom")


def _upload(
    filename: str = "clip.mp3",
    media_kind: str = "audio",
    content: bytes = SAMPLE_MP3,
    category: str = "domestic_us",
):
    return client.post(
        "/v1/analyze/media",
        files={"file": (filename, BytesIO(content), "audio/mpeg")},
        data={
            "user_selected_category": category,
            "media_kind": media_kind,
            "title": "Demo upload",
            "source_url": "https://example.com/reel/demo",
        },
    )


def test_media_upload_success_mock_transcription():
    r = _upload()
    assert r.status_code == 200
    data = r.json()
    assert data["analysis_id"]
    assert data["media_source"]["input_basis"] == "uploaded_audio_transcript"
    assert data["media_source"]["transcription_provider"]
    assert "uploaded media" in data["media_source"]["transparency_note"].lower()
    assert data["generated_transcript"]
    assert MOCK_TRANSCRIPT.split(".")[0][:40] in data["generated_transcript"]
    assert len(data["claims"]) >= 0
    assert any("uploaded media" in n.lower() for n in data["notes"])


def test_media_upload_screen_recording_basis():
    r = _upload(filename="screen.mp4", media_kind="screen_recording")
    assert r.status_code == 200
    assert r.json()["media_source"]["input_basis"] == "uploaded_screen_recording_transcript"


def test_media_upload_unsupported_file_type():
    r = _upload(filename="notes.txt", media_kind="audio")
    assert r.status_code == 415
    assert "Unsupported" in r.json()["detail"]


def test_media_upload_transcription_failure():
    from app import main

    original = main._media
    main._media = MediaIngestService(
        ingest=original._ingest,
        transcription=FailingTranscriptionProvider(),
    )
    try:
        r = _upload()
        assert r.status_code == 422
        assert "unavailable" in r.json()["detail"].lower()
    finally:
        main._media = original


def test_media_upload_passes_transcript_to_analysis_pipeline():
    from app import main

    original = main._media
    mock_ingest = MagicMock()
    mock_ingest.run_analysis.return_value = original._ingest.run_analysis(
        MOCK_TRANSCRIPT,
        "transcript",
        "domestic_us",
    )
    main._media = MediaIngestService(
        ingest=mock_ingest,
        transcription=CustomTranscriptionProvider(),
    )
    try:
        r = _upload()
        assert r.status_code == 200
        mock_ingest.run_analysis.assert_called_once()
        args, kwargs = mock_ingest.run_analysis.call_args
        text = kwargs.get("text") or (args[0] if args else "")
        assert MOCK_TRANSCRIPT in text
        content_type = kwargs.get("content_type") or (args[1] if len(args) > 1 else "")
        assert content_type == "transcript"
    finally:
        main._media = original


def test_media_upload_persisted_and_loadable():
    r = _upload()
    assert r.status_code == 200
    aid = r.json()["analysis_id"]
    get_r = client.get(f"/v1/analysis/{aid}")
    assert get_r.status_code == 200
    assert get_r.json()["media_source"]["input_basis"] == "uploaded_audio_transcript"
