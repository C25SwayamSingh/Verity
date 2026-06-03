import type { FramingResult } from "@/lib/types";

interface FramingPanelProps {
  framing: FramingResult;
  eligible: boolean;
}

export default function FramingPanel({ framing, eligible }: FramingPanelProps) {
  if (!eligible) {
    return (
      <section className="rounded-lg border border-slate-200 bg-slate-50 p-5">
        <h2 className="text-sm font-semibold text-giver-ink">Framing indicators</h2>
        <p className="mt-2 text-sm text-giver-slate">
          Framing analysis is not available for this content based on eligibility rules.
        </p>
      </section>
    );
  }

  const label = framing.overall_label.replace(/_/g, " ");

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="text-sm font-semibold text-giver-ink">Framing indicators</h2>
      <p className="mt-1 text-sm capitalize text-giver-slate">Overall: {label}</p>
      {framing.indicators.length === 0 ? (
        <p className="mt-3 text-sm text-giver-slate">No notable framing signals detected.</p>
      ) : (
        <ul className="mt-3 space-y-3">
          {framing.indicators.map((ind, i) => (
            <li key={i} className="rounded-md bg-giver-mist p-3 text-sm">
              <p className="font-medium capitalize text-giver-ink">
                {ind.indicator_type.replace(/_/g, " ")}
              </p>
              <p className="mt-1 text-giver-slate">{ind.description}</p>
              {ind.examples.length > 0 && (
                <p className="mt-1 text-xs text-giver-slate">
                  Examples: {ind.examples.join(", ")}
                </p>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
