import type { MetricVariant } from "@/lib/creatorDisplay";
import { scorePercent } from "@/lib/creatorDisplay";

interface Props {
  label: string;
  value: number;
  help: string;
  variant?: MetricVariant;
}

export default function CreatorMetricBar({
  label,
  value,
  help,
  variant = "neutral",
}: Props) {
  const pct = scorePercent(value);
  let barColor: string;
  let textColor: string;

  if (variant === "warn") {
    barColor = pct <= 15 ? "bg-giver-ok" : pct <= 30 ? "bg-amber-500" : "bg-giver-warn";
    textColor = pct <= 15 ? "text-giver-ok" : pct <= 30 ? "text-amber-700" : "text-giver-warn";
  } else {
    barColor = pct >= 75 ? "bg-giver-ok" : pct >= 55 ? "bg-giver-accent" : "bg-giver-warn";
    textColor = pct >= 75 ? "text-giver-ok" : pct >= 55 ? "text-giver-accent" : "text-giver-warn";
  }

  return (
    <div className="rounded-md border border-slate-100 bg-white px-3 py-2.5 space-y-1.5">
      <div className="flex items-center gap-3">
        <div className="min-w-0 flex-1">
          <p className="text-xs font-medium text-giver-ink">{label}</p>
          <p className="text-[10px] text-giver-low mt-0.5 leading-snug">{help}</p>
        </div>
        <span className={`shrink-0 text-lg font-bold tabular-nums ${textColor}`}>{pct}</span>
      </div>
      <div className="h-2 rounded-full bg-slate-200">
        <div className={`h-2 rounded-full ${barColor}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
