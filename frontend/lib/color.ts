import type { CorroborationStatus } from "./types";

export function corroborationColor(status: CorroborationStatus): string {
  switch (status) {
    case "high_corroboration":
      return "bg-emerald-100 text-emerald-900 border-emerald-200";
    case "medium_corroboration":
      return "bg-sky-100 text-sky-900 border-sky-200";
    case "low_corroboration":
      return "bg-amber-100 text-amber-900 border-amber-200";
    case "contradicted":
      return "bg-rose-100 text-rose-900 border-rose-200";
    default:
      return "bg-slate-100 text-slate-700 border-slate-200";
  }
}

export function corroborationLabel(status: CorroborationStatus): string {
  const labels: Record<CorroborationStatus, string> = {
    high_corroboration: "High corroboration",
    medium_corroboration: "Medium corroboration",
    low_corroboration: "Low corroboration",
    contradicted: "Contradicted by available sources",
    not_checkable: "Not checkable",
  };
  return labels[status] ?? status;
}

export function claimTypeLabel(t: string): string {
  return t.replace(/_/g, " ");
}
