import type { DashboardArticle } from "@/lib/types";

interface Props {
  article: DashboardArticle;
  rank: number;
}

const FRAMING_STYLES: Record<string, string> = {
  mostly_neutral: "bg-emerald-50 text-emerald-700 border-emerald-200",
  mixed_framing: "bg-amber-50 text-amber-700 border-amber-200",
  notable_framing: "bg-red-50 text-red-700 border-red-200",
};

const FRAMING_LABELS: Record<string, string> = {
  mostly_neutral: "Mostly neutral",
  mixed_framing: "Mixed framing",
  notable_framing: "Notable framing",
};

const SCORE_DEFINITIONS: {
  key: keyof DashboardArticle;
  label: string;
  weight: string;
}[] = [
  { key: "importance_score", label: "Importance", weight: "35%" },
  { key: "credibility_score", label: "Credibility", weight: "30%" },
  { key: "relevance_score", label: "Relevance", weight: "20%" },
  { key: "freshness_score", label: "Freshness", weight: "10%" },
  { key: "source_diversity_score", label: "Diversity", weight: "5%" },
];

function ScoreBar({
  label,
  weight,
  value,
}: {
  label: string;
  weight: string;
  value: number;
}) {
  const pct = Math.round(value * 100);
  const barColor =
    pct >= 85
      ? "bg-giver-ok"
      : pct >= 65
        ? "bg-giver-accent"
        : "bg-giver-warn";

  return (
    <div className="flex min-w-0 flex-col gap-0.5">
      <div className="flex items-baseline justify-between gap-1">
        <span className="text-[10px] font-medium text-giver-ink">{label}</span>
        <span className="text-[10px] text-giver-low">{weight}</span>
      </div>
      <div className="h-1.5 w-full rounded-full bg-slate-200">
        <div
          className={`h-1.5 rounded-full ${barColor}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-[10px] font-semibold text-giver-slate">{pct}</span>
    </div>
  );
}

function formatDate(iso: string): string {
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

export default function DashboardArticleCard({ article, rank }: Props) {
  const framingStyle =
    FRAMING_STYLES[article.framing_label] ?? "bg-slate-50 text-slate-600 border-slate-200";
  const framingText = FRAMING_LABELS[article.framing_label] ?? article.framing_label;
  const finalPct = Math.round(article.final_score * 100);
  const finalColor =
    finalPct >= 85
      ? "text-giver-ok"
      : finalPct >= 70
        ? "text-giver-accent"
        : "text-giver-warn";

  return (
    <article className="rounded-lg border border-slate-200 bg-white shadow-sm">

      {/* Header row */}
      <div className="flex items-start gap-3 p-5">
        <span className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-giver-accent text-xs font-bold text-white">
          {rank}
        </span>
        <div className="min-w-0 flex-1">
          <h3 className="text-sm font-semibold leading-snug text-giver-ink">
            {article.headline}
          </h3>
          <p className="mt-1 text-xs text-giver-low">
            {article.source} · {formatDate(article.published_at)}
          </p>
        </div>
        <div className="shrink-0 text-right">
          <span className={`text-2xl font-bold ${finalColor}`}>{finalPct}</span>
          <span className="ml-0.5 text-xs text-giver-low">/100</span>
          <p className="text-[10px] text-giver-low">final score</p>
        </div>
      </div>

      {/* Summary */}
      <div className="border-t border-slate-100 px-5 py-3">
        <p className="text-sm leading-relaxed text-giver-slate">{article.neutral_summary}</p>
      </div>

      {/* Score bars */}
      <div className="border-t border-slate-100 bg-giver-mist px-5 py-3">
        <p className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-giver-low">
          Component scores
        </p>
        <div className="grid grid-cols-5 gap-3">
          {SCORE_DEFINITIONS.map(({ key, label, weight }) => (
            <ScoreBar
              key={key}
              label={label}
              weight={weight}
              value={article[key] as number}
            />
          ))}
        </div>
      </div>

      {/* Framing + claims + support */}
      <div className="border-t border-slate-100 px-5 py-3 space-y-3">

        {/* Framing badge */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-medium text-giver-ink">Framing:</span>
          <span
            className={`inline-flex items-center rounded border px-2 py-0.5 text-xs font-medium ${framingStyle}`}
          >
            {framingText}
          </span>
        </div>

        {/* Key claims */}
        {article.key_claims.length > 0 && (
          <div>
            <p className="text-xs font-medium text-giver-ink">Key claims</p>
            <ul className="mt-1 list-disc space-y-0.5 pl-4 text-xs text-giver-slate">
              {article.key_claims.map((claim, i) => (
                <li key={i}>{claim}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Support + contradiction */}
        <div className="space-y-1">
          <p className="text-xs text-giver-slate">
            <span className="font-medium text-giver-ink">Support: </span>
            {article.support_summary}
          </p>
          {article.contradiction_warnings.length > 0 &&
            article.contradiction_warnings.map((w, i) => (
              <p key={i} className="text-xs text-giver-warn">
                <span className="font-medium">Caution: </span>
                {w}
              </p>
            ))}
        </div>

        {/* Why selected */}
        <p className="text-xs text-giver-low">
          <span className="font-medium text-giver-ink not-italic">Why selected: </span>
          {article.why_selected}
        </p>
      </div>
    </article>
  );
}
