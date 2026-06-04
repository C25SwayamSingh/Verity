"""Upload user-provided media → transcript → existing checker pipeline."""

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from sqlmodel import Session

from app.core.config import get_settings
from app.core.media_input_basis import (
    MEDIA_TRANSPARENCY_NOTE,
    media_input_basis_label,
    media_kind_to_input_basis,
)
from app.db.models import AnalysisRecord
from app.schemas.domain import AnalyzeResponse, MediaSourceMetadata
from app.services.ingest_service import IngestService
from app.services.transcription.base import TranscriptionError, TranscriptionProvider
from app.services.transcription.registry import get_transcription_provider

VIDEO_EXTENSIONS = {".mp4", ".mov"}
AUDIO_EXTENSIONS = {".m4a", ".mp3", ".wav"}
ALLOWED_EXTENSIONS = VIDEO_EXTENSIONS | AUDIO_EXTENSIONS

EXTENSION_TO_MEDIA_KIND = {
    ".mp4": "video",
    ".mov": "video",
    ".m4a": "audio",
    ".mp3": "audio",
    ".wav": "audio",
}


class UnsupportedMediaTypeError(Exception):
    pass


class MediaTooLargeError(Exception):
    pass


class MediaIngestService:
    def __init__(
        self,
        ingest: Optional[IngestService] = None,
        transcription: Optional[TranscriptionProvider] = None,
    ) -> None:
        self._ingest = ingest or IngestService()
        self._transcription = transcription or get_transcription_provider()
        self._settings = get_settings()

    def analyze_upload(
        self,
        *,
        file_bytes: bytes,
        filename: str,
        media_kind: str,
        user_selected_category: str,
        title: str = "",
        source_url: str = "",
        session: Session,
    ) -> AnalyzeResponse:
        self._validate_size(len(file_bytes))
        suffix = Path(filename).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise UnsupportedMediaTypeError(
                f"Unsupported file type '{suffix or '(none)'}'. "
                f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )

        inferred = EXTENSION_TO_MEDIA_KIND.get(suffix, "video")
        if media_kind not in ("video", "audio", "screen_recording"):
            media_kind = inferred
        if media_kind == "screen_recording" and suffix not in VIDEO_EXTENSIONS:
            raise UnsupportedMediaTypeError(
                "Screen recordings should be uploaded as mp4 or mov video files."
            )

        input_basis = media_kind_to_input_basis(media_kind)

        with tempfile.TemporaryDirectory(prefix="giver_media_") as tmp:
            tmp_path = Path(tmp)
            upload_path = tmp_path / f"upload{suffix}"
            upload_path.write_bytes(file_bytes)

            audio_path = self._prepare_audio(upload_path, suffix, tmp_path)
            try:
                tx = self._transcription.transcribe(audio_path)
            except TranscriptionError:
                raise

        transcript = self._build_transcript_text(
            tx.text,
            title=title,
            source_url=source_url,
            filename=filename,
        )

        base = self._ingest.run_analysis(
            text=transcript,
            content_type="transcript",
            user_selected_category=user_selected_category,
        )

        metadata = MediaSourceMetadata(
            input_basis=input_basis,
            input_basis_label=media_input_basis_label(input_basis) or input_basis,
            transparency_note=MEDIA_TRANSPARENCY_NOTE,
            original_filename=filename,
            source_url=source_url.strip(),
            title=title.strip(),
            transcript_char_count=len(transcript),
            transcription_provider=tx.provider,
            media_kind=media_kind,
        )

        notes = [MEDIA_TRANSPARENCY_NOTE]
        if title.strip():
            notes.append(f"Upload title: {title.strip()}")
        if source_url.strip():
            notes.append(
                "Original link stored as metadata only — The Giver does not download or scrape linked videos."
            )
        notes.extend(base.notes)

        enriched = base.model_copy(
            update={
                "notes": notes,
                "media_source": metadata,
                "generated_transcript": transcript,
            }
        )

        record = AnalysisRecord(
            id=enriched.analysis_id,
            request_text=transcript[:10000],
            content_type="transcript",
            user_selected_category=user_selected_category,
            result_json=enriched.model_dump_json(),
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        return enriched

    def _validate_size(self, size: int) -> None:
        if size > self._settings.media_max_upload_bytes:
            mb = self._settings.media_max_upload_bytes // (1024 * 1024)
            raise MediaTooLargeError(f"File exceeds maximum upload size of {mb} MB.")

    def _prepare_audio(self, upload_path: Path, suffix: str, tmp_path: Path) -> Path:
        if suffix in AUDIO_EXTENSIONS:
            return upload_path

        if self._settings.transcription_provider == "mock":
            wav = tmp_path / "audio.wav"
            wav.write_bytes(b"")
            return wav

        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            raise TranscriptionError(
                "Video upload requires ffmpeg to extract audio. "
                "Install ffmpeg, upload audio-only (mp3/m4a/wav), or set TRANSCRIPTION_PROVIDER=mock for development."
            )

        out_path = tmp_path / "extracted.wav"
        cmd = [
            ffmpeg,
            "-y",
            "-i",
            str(upload_path),
            "-vn",
            "-acodec",
            "pcm_s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            str(out_path),
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=120)
        except subprocess.CalledProcessError as exc:
            stderr = (exc.stderr or b"").decode("utf-8", errors="replace")[:500]
            raise TranscriptionError(f"Could not extract audio from video: {stderr}") from exc
        except subprocess.TimeoutExpired as exc:
            raise TranscriptionError("Audio extraction timed out.") from exc

        if not out_path.is_file() or out_path.stat().st_size == 0:
            raise TranscriptionError("No audio track found in uploaded video.")
        return out_path

    def _build_transcript_text(
        self,
        body: str,
        *,
        title: str,
        source_url: str,
        filename: str,
    ) -> str:
        parts: list[str] = []
        if title.strip():
            parts.append(f"Title: {title.strip()}")
        if source_url.strip():
            parts.append(f"Source link (metadata only): {source_url.strip()}")
        parts.append(f"Uploaded file: {filename}")
        parts.append(body.strip())
        return "\n\n".join(parts)
