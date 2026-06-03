import type { SourceRef } from "@/lib/types";

interface SourceAlignmentPanelProps {
  supporting: SourceRef[];
  contradicting: SourceRef[];
}

function SourceList({
  title,
  sources,
  variant,
}: {
  title: string;
  sources: SourceRef[];
  variant: "support" | "contradict";
}) {
  if (sources.length === 0) return null;
  const border =
    variant === "support" ? "border-emerald-100" : "border-rose-100";
  return (
    <div className={`mt-3 rounded-md border ${border} p-3`}>
      <p className="text-xs font-semibold uppercase tracking-wide text-giver-slate">
        {title}
      </p>
      <ul className="mt-2 space-y-2">
        {sources.map((s) => (
          <li key={s.source_id} className="text-xs">
            <span className="font-medium text-giver-ink">{s.title}</span>
            <span className="text-giver-slate"> — {s.publisher}</span>
            <p className="mt-0.5 text-giver-slate">{s.snippet}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function SourceAlignmentPanel({
  supporting,
  contradicting,
}: SourceAlignmentPanelProps) {
  if (supporting.length === 0 && contradicting.length === 0) {
    return (
      <p className="mt-3 text-xs italic text-giver-slate">
        No fixture source alignment found for this claim.
      </p>
    );
  }
  return (
    <div>
      <SourceList title="Supporting sources (fixtures)" sources={supporting} variant="support" />
      <SourceList
        title="Contradicting sources (fixtures)"
        sources={contradicting}
        variant="contradict"
      />
    </div>
  );
}
