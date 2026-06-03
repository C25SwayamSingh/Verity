import type { AnalyzeResponse } from "@/lib/types";
import ClaimCard from "./ClaimCard";
import FramingPanel from "./FramingPanel";
import NeutralRewrite from "./NeutralRewrite";

interface ResultsDashboardProps {
  data: AnalyzeResponse;
}

export default function ResultsDashboard({ data }: ResultsDashboardProps) {
  const eligible = data.eligibility.bias_framing_eligible;

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-sm font-semibold text-giver-ink">Summary</h2>
        <p className="mt-2 text-sm leading-relaxed text-giver-slate">{data.summary}</p>
      </section>

      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-sm font-semibold text-giver-ink">Key takeaways</h2>
        <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-giver-slate">
          {data.key_takeaways.map((t, i) => (
            <li key={i}>{t}</li>
          ))}
        </ul>
      </section>

      <section
        className={`rounded-lg border p-5 ${
          eligible ? "border-emerald-200 bg-emerald-50" : "border-amber-200 bg-amber-50"
        }`}
      >
        <h2 className="text-sm font-semibold text-giver-ink">Content eligibility</h2>
        <p className="mt-1 text-xs text-giver-slate">
          Detected category: <strong>{data.eligibility.detected_category}</strong>
          {" · "}
          Framing &amp; alignment:{" "}
          <strong>{eligible ? "available" : "not available"}</strong>
        </p>
        <p className="mt-2 text-sm text-giver-slate">{data.eligibility.reason}</p>
      </section>

      {data.notes && data.notes.length > 0 && (
        <section className="rounded-lg border border-slate-200 bg-white p-5">
          <h2 className="text-sm font-semibold text-giver-ink">Notes</h2>
          <ul className="mt-2 list-disc pl-5 text-sm text-giver-slate">
            {data.notes.map((n, i) => (
              <li key={i}>{n}</li>
            ))}
          </ul>
        </section>
      )}

      <section>
        <h2 className="mb-3 text-sm font-semibold text-giver-ink">
          Extracted claims &amp; cross-source corroboration
        </h2>
        <div className="space-y-4">
          {data.claims.map((c) => (
            <ClaimCard key={c.claim_id} claim={c} showAlignment={eligible} />
          ))}
        </div>
      </section>

      <FramingPanel framing={data.framing} eligible={eligible} />
      <NeutralRewrite text={data.neutral_rewrite} eligible={eligible} />
    </div>
  );
}
