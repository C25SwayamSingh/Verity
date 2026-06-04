import { CREATOR_DISCLAIMER } from "@/lib/creatorDisplay";

interface Props {
  compact?: boolean;
}

export default function CreatorDisclaimer({ compact = false }: Props) {
  if (compact) {
    return (
      <p className="text-xs text-giver-slate leading-relaxed border-l-2 border-giver-accent/40 pl-3">
        {CREATOR_DISCLAIMER}
      </p>
    );
  }

  return (
    <div
      className="rounded-lg border border-slate-200 bg-giver-mist px-4 py-3"
      role="note"
      aria-label="Integrity measurement disclaimer"
    >
      <p className="text-xs font-semibold uppercase tracking-wide text-giver-low mb-1">
        How to read this report
      </p>
      <p className="text-sm text-giver-slate leading-relaxed">{CREATOR_DISCLAIMER}</p>
    </div>
  );
}
