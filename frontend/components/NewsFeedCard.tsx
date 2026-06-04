import Link from "next/link";
import type { NewsFeedItem } from "@/lib/types";

const CORROBORATION_STYLES: Record<string, string> = {
  strong: "bg-emerald-50 text-emerald-700 border-emerald-200",
  moderate: "bg-sky-50 text-sky-700 border-sky-200",
  limited: "bg-amber-50 text-amber-700 border-amber-200",
  single_source: "bg-slate-50 text-slate-600 border-slate-200",
};

const FRAMING_STYLES: Record<string, string> = {
  neutral: "bg-emerald-50 text-emerald-700 border-emerald-200",
  mixed: "bg-amber-50 text-amber-700 border-amber-200",
  notable: "bg-red-50 text-red-700 border-red-200",
  unknown: "bg-slate-50 text-slate-600 border-slate-200",
};

const CONFIDENCE_STYLES: Record<string, string> = {
  high: "text-giver-ok",
  medium: "text-giver-accent",
  low: "text-giver-warn",
};

const CATEGORY_LABELS: Record<string, string> = {
  breaking: "Breaking",
  domestic_us: "Domestic / U.S.",
  foreign_world: "Foreign / World",
  markets_stocks: "Markets / Stocks",
  tech_ai: "Tech & AI",
};

function formatTime(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

export default function NewsFeedCard({ item }: { item: NewsFeedItem }) {
  const corrStyle =
    CORROBORATION_STYLES[item.corroboration.level] ?? CORROBORATION_STYLES.single_source;
  const framingStyle = FRAMING_STYLES[item.framing.level] ?? FRAMING_STYLES.unknown;
  const confidenceStyle = CONFIDENCE_STYLES[item.confidence.level] ?? "text-giver-slate";

  return (
    <article className="flex flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      {/* Header */}
      <div className="flex items-start justify-between gap-3 px-5 pt-5">
        <div className="min-w-0">
          <span className="inline-flex items-center rounded-full bg-giver-mist px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-giver-low">
            {CATEGORY_LABELS[item.category] ?? item.category}
          </span>
          <h3 className="mt-2 text-lg font-semibold leading-snug text-giver-ink">
            {item.headline}
          </h3>
          <p className="mt-1 text-xs text-giver-low">
            {item.source} · {formatTime(item.published_at)}
          </p>
        </div>
        <div className="shrink-0 text-right">
          <span className={`text-sm font-bold ${confidenceStyle}`}>
            {Math.round(item.confidence.score * 100)}
          </span>
          <p className="text-[10px] text-giver-low">confidence</p>
        </div>
      </div>

      {/* Neutral summary */}
      <div className="px-5 pt-3">
        <p className="text-sm leading-relaxed text-giver-slate">{item.neutral_summary}</p>
      </div>

      {/* Integrity signals */}
      <div className="mt-4 space-y-2 border-t border-slate-100 bg-giver-mist px-5 py-3">
        <div className="flex flex-wrap gap-2">
          <span
            className={`inline-flex items-center rounded border px-2 py-0.5 text-xs font-medium ${corrStyle}`}
          >
            {item.corroboration.label}
          </span>
          <span
            className={`inline-flex items-center rounded border px-2 py-0.5 text-xs font-medium ${framingStyle}`}
          >
            {item.framing.label}
          </span>
          {item.contradiction.present && (
            <span className="inline-flex items-center rounded border border-red-200 bg-red-50 px-2 py-0.5 text-xs font-medium text-red-700">
              {item.contradiction.label}
            </span>
          )}
        </div>

        {item.corroboration.detail && (
          <p className="text-xs text-giver-slate">
            <span className="font-medium text-giver-ink">Source alignment: </span>
            {item.corroboration.detail}
          </p>
        )}
        {item.contradiction.present && item.contradiction.detail && (
          <p className="text-xs text-giver-warn">
            <span className="font-medium">Caution: </span>
            {item.contradiction.detail}
          </p>
        )}
        <p className="text-xs text-giver-low">
          <span className="font-medium text-giver-ink">Why this story appears here: </span>
          {item.why_selected}
        </p>
      </div>

      {/* Footer link */}
      <div className="flex items-center justify-between px-5 py-3">
        <Link
          href={item.detail_path}
          className="text-xs font-medium text-giver-accent hover:underline"
        >
          Open full analysis →
        </Link>
        <Link
          href="/check"
          className="text-xs font-medium text-giver-low hover:text-giver-accent"
        >
          Check your own
        </Link>
      </div>
    </article>
  );
}
