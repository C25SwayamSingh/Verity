/** Shared copy and styles for Creator Integrity Dashboard (Phase 3.7). */

export const CREATOR_DISCLAIMER =
  "Verity measures source alignment, claim support, and framing indicators. It does not determine absolute truth.";

export const CREATOR_LIST_INTRO =
  "Sample integrity profiles for information-focused creators. Each report summarizes cross-source corroboration, contradiction signals, and framing patterns from analyzed posts—not a verdict on the creator.";

export type MetricVariant = "neutral" | "warn";

export interface MetricDefinition {
  key: string;
  label: string;
  help: string;
  variant: MetricVariant;
  higherIsBetter: boolean;
}

export const CREATOR_METRICS: MetricDefinition[] = [
  {
    key: "source_alignment_score",
    label: "Source alignment score",
    help: "How closely extracted claims align with cited or cross-referenced sources across analyzed posts. Higher values suggest stronger source transparency.",
    variant: "neutral",
    higherIsBetter: true,
  },
  {
    key: "claim_support_rate",
    label: "Claim support rate",
    help: "Share of checkable claims with medium or high cross-source corroboration. Reflects how often statements are backed by independent sources.",
    variant: "neutral",
    higherIsBetter: true,
  },
  {
    key: "contradiction_rate",
    label: "Contradiction rate",
    help: "Share of checkable claims where cross-source evidence shows contradiction signals. Useful for spotting statements that diverge from reporting elsewhere.",
    variant: "warn",
    higherIsBetter: false,
  },
  {
    key: "low_corroboration_rate",
    label: "Low corroboration rate",
    help: "Share of checkable claims with limited supporting sources. May indicate areas where additional sourcing would improve information integrity.",
    variant: "warn",
    higherIsBetter: false,
  },
  {
    key: "source_diversity_score",
    label: "Source diversity score",
    help: "Breadth of independent publishers referenced across posts. Higher values suggest a wider range of sources, not repetition of a single outlet.",
    variant: "neutral",
    higherIsBetter: true,
  },
  {
    key: "average_framing_score",
    label: "Average framing score",
    help: "Composite neutrality of language and presentation across posts. Higher values correspond to mostly neutral framing; lower values suggest more notable framing indicators.",
    variant: "neutral",
    higherIsBetter: true,
  },
];

export const FRAMING_STYLES: Record<string, string> = {
  mostly_neutral: "bg-emerald-50 text-emerald-700 border-emerald-200",
  mixed_framing: "bg-amber-50 text-amber-700 border-amber-200",
  notable_framing: "bg-red-50 text-red-700 border-red-200",
};

export const FRAMING_LABELS: Record<string, string> = {
  mostly_neutral: "Mostly neutral",
  mixed_framing: "Mixed framing",
  notable_framing: "Notable framing",
};

export const CORROBORATION_STYLES: Record<string, string> = {
  high_corroboration: "bg-emerald-50 text-emerald-700 border-emerald-200",
  medium_corroboration: "bg-blue-50 text-blue-700 border-blue-200",
  low_corroboration: "bg-amber-50 text-amber-700 border-amber-200",
  contradicted: "bg-red-50 text-red-700 border-red-200",
  not_checkable: "bg-slate-50 text-slate-500 border-slate-200",
};

export const CORROBORATION_LABELS: Record<string, string> = {
  high_corroboration: "High corroboration",
  medium_corroboration: "Medium corroboration",
  low_corroboration: "Low corroboration",
  contradicted: "Contradiction signal",
  not_checkable: "Not checkable",
};

export const CATEGORY_LABELS: Record<string, string> = {
  breaking: "Breaking",
  domestic_us: "Domestic / U.S.",
  foreign_world: "Foreign / World",
  markets_stocks: "Markets / Stocks",
  tech_ai: "Tech & AI",
  other: "Other",
};

export function formatCreatorDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  } catch {
    return iso;
  }
}

export function scorePercent(value: number): number {
  return Math.round(value * 100);
}
