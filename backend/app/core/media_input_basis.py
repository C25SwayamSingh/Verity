"""Input basis for uploaded media transcripts (Phase 4A)."""

from typing import Literal, Optional

MediaInputBasis = Literal[
    "uploaded_video_transcript",
    "uploaded_audio_transcript",
    "uploaded_screen_recording_transcript",
]

MEDIA_INPUT_BASIS_LABELS: dict[str, str] = {
    "uploaded_video_transcript": "Uploaded video transcript",
    "uploaded_audio_transcript": "Uploaded audio transcript",
    "uploaded_screen_recording_transcript": "Uploaded screen recording transcript",
}

MEDIA_TRANSPARENCY_NOTE = (
    "Analysis based on transcript generated from uploaded media. "
    "The Giver did not download, scrape, or verify content from social platforms."
)


def media_kind_to_input_basis(media_kind: str) -> str:
    mapping = {
        "video": "uploaded_video_transcript",
        "audio": "uploaded_audio_transcript",
        "screen_recording": "uploaded_screen_recording_transcript",
    }
    return mapping.get(media_kind, "uploaded_video_transcript")


def media_input_basis_label(basis: Optional[str]) -> Optional[str]:
    if not basis:
        return None
    return MEDIA_INPUT_BASIS_LABELS.get(basis, basis.replace("_", " "))
