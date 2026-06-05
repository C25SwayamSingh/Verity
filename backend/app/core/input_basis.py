"""Input basis labels for demo creator posts (transparency, not ingestion)."""

from typing import Literal, Optional

InputBasis = Literal[
    "full_transcript",
    "manual_rough_transcript",
    "caption_text",
    "third_party_extracted_key_points",
    "manual_summary_source_notes",
]

DEFAULT_INPUT_BASIS: InputBasis = "third_party_extracted_key_points"

VERBATIM_INPUT_BASES = frozenset({"full_transcript"})

INPUT_BASIS_LABELS: dict[str, str] = {
    "full_transcript": "Full transcript",
    "manual_rough_transcript": "Manual rough transcript",
    "caption_text": "Caption text",
    "third_party_extracted_key_points": "Third-party extracted key points",
    "manual_summary_source_notes": "Manual summary / source notes",
}


def input_basis_label(basis: Optional[str]) -> Optional[str]:
    if not basis:
        return None
    return INPUT_BASIS_LABELS.get(basis, basis.replace("_", " "))


def is_non_verbatim_input_basis(basis: Optional[str]) -> bool:
    return bool(basis and basis not in VERBATIM_INPUT_BASES)


def input_basis_transparency_note(basis: Optional[str]) -> Optional[str]:
    """Short UI note when analysis is not from a verbatim transcript."""
    if not is_non_verbatim_input_basis(basis):
        return None
    if basis == "third_party_extracted_key_points":
        return (
            "Analysis based on third-party extracted key points (e.g. Fofo-style notes), "
            "not a verbatim transcript. Verity did not watch or transcribe the original video."
        )
    if basis == "caption_text":
        return (
            "Analysis based on caption text, not a verbatim transcript. "
            "Verity did not watch or transcribe the original video."
        )
    if basis == "manual_rough_transcript":
        return (
            "Analysis based on a manual rough transcript, not a verified verbatim transcript. "
            "Verity analyzes the submitted text only."
        )
    return (
        "Analysis based on provided source notes, not a verbatim transcript. "
        "Verity did not watch or transcribe the original video."
    )
