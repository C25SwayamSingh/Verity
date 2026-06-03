import { claimTypeLabel, corroborationColor, corroborationLabel } from "@/lib/color";
import type { ClaimResult } from "@/lib/types";
import SourceAlignmentPanel from "./SourceAlignmentPanel";

interface ClaimCardProps {
  claim: ClaimResult;
  showAlignment: boolean;
}

export default function ClaimCard({ claim, showAlignment }: ClaimCardProps) {
  return (
    <article className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-sm leading-relaxed text-giver-ink">{claim.text}</p>
      <div className="mt-3 flex flex-wrap gap-2">
        <span className="rounded-full border border-slate-200 bg-slate-50 px-2.5 py-0.5 text-xs capitalize text-giver-slate">
          {claimTypeLabel(claim.claim_type)}
        </span>
        <span
          className={`rounded-full border px-2.5 py-0.5 text-xs font-medium ${corroborationColor(
            claim.corroboration_status,
          )}`}
        >
          {corroborationLabel(claim.corroboration_status)}
        </span>
      </div>
      <p className="mt-3 text-xs text-giver-slate">{claim.explanation}</p>
      {showAlignment && (
        <SourceAlignmentPanel
          supporting={claim.supporting_sources}
          contradicting={claim.contradicting_sources}
        />
      )}
    </article>
  );
}
