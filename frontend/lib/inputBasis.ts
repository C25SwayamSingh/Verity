/** Demo post input basis — transparency labels (must match backend slugs). */

export type InputBasis =
  | "full_transcript"
  | "manual_rough_transcript"
  | "caption_text"
  | "third_party_extracted_key_points"
  | "manual_summary_source_notes";

export const DEFAULT_INPUT_BASIS: InputBasis = "third_party_extracted_key_points";

export const INPUT_BASIS_OPTIONS: { value: InputBasis; label: string; hint: string }[] = [
  {
    value: "full_transcript",
    label: "Full transcript",
    hint: "Use when you have a complete verbatim transcript of the original audio/video.",
  },
  {
    value: "manual_rough_transcript",
    label: "Manual rough transcript",
    hint: "Hand-typed or partial transcript; not verified word-for-word.",
  },
  {
    value: "caption_text",
    label: "Caption text",
    hint: "Platform caption only; may omit spoken content.",
  },
  {
    value: "third_party_extracted_key_points",
    label: "Third-party extracted key points",
    hint: "e.g. Fofo-style bullet notes — not an official transcript.",
  },
  {
    value: "manual_summary_source_notes",
    label: "Manual summary / source notes",
    hint: "Your own summary of what the post discussed.",
  },
];

export function inputBasisFormHelp(basis: InputBasis): string {
  return INPUT_BASIS_OPTIONS.find((o) => o.value === basis)?.hint ?? "";
}
