"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import ErrorState from "@/components/ErrorState";
import LoadingState from "@/components/LoadingState";
import { getDashboardArticle } from "@/lib/api";
import type { DashboardArticle } from "@/lib/types";

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

const CATEGORY_LABELS: Record<string, string> = {
  breaking: "Breaking",
  domestic_us: "Domestic / U.S.",
  foreign_world: "Foreign / World",
  markets_stocks: "Markets / Stocks",
  tech_ai: "Tech & AI",
};

function ScoreRow({
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
    pct >= 85 ? "bg-giver-ok" : pct >= 65 ? "bg-giver-accent" : "bg-giver-warn";
  const textColor =
    pct >= 85 ? "text-giver-ok" : pct >= 65 ? "text-giver-accent" : "text-giver-warn";

  return (
    <div className="flex items-center gap-3">
      <div className="w-28 shrink-0 text-xs font-medium text-giver-ink">{label}</div>
      <div className="w-8 shrink-0 text-right text-[10px] text-giver-low">{weight}</div>
      <div className="flex-1 h-2 rounded-full bg-slate-200">
        <div className={`h-2 rounded-full ${barColor}`} style={{ width: `${pct}%` }} />
      </div>
      <span className={`w-7 shrink-0 text-right text-xs font-semibold ${textColor}`}>
        {pct}
      </span>
    </div>
  );
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  } catch {
    return iso;
  }
}

export default function DashboardArticleDetailPage() {
  const params = useParams();
  const id = typeof params.id === "string" ? params.id : "";

  const [article, setArticle] = useState<DashboardArticle | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    getDashboardArticle(id)
      .then(setArticle)
      .catch((e) => setError(e instanceof Error ? e.message : "Article not found."))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <LoadingState />;
  if (error) {
    return (
      <div className="space-y-4">
        <Link href="/dashboard" className="text-sm text-giver-accent hover:underline">
          ← Back to Dashboard
        </Link>
        <ErrorState message={error} />
      </div>
    );
  }
  if (!article) return null;

  const framingStyle =
    FRAMING_STYLES[article.framing_label] ?? "bg-slate-50 text-slate-600 border-slate-200";
  const framingText = FRAMING_LABELS[article.framing_label] ?? article.framing_label;
  const finalPct = Math.round(article.final_score * 100);
  const finalColor =
    finalPct >= 85 ? "text-giver-ok" : finalPct >= 70 ? "text-giver-accent" : "text-giver-warn";

  return (
    <div className="space-y-6">

      {/* Back nav */}
      <Link href="/dashboard" className="inline-block text-sm text-giver-accent hover:underline">
        ← Back to Dashboard
      </Link>

      {/* Header */}
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0 flex-1">
            <h2 className="text-lg font-semibold leading-snug text-giver-ink">
              {article.headline}
            </h2>
            <p className="mt-1 text-sm text-giver-low">
              {article.source}
              {" · "}
              {CATEGORY_LABELS[article.category] ?? article.category}
              {" · "}
              {formatDate(article.published_at)}
            </p>
          </div>
          <div className="shrink-0 text-right">
            <span className={`text-3xl font-bold ${finalColor}`}>{finalPct}</span>
            <span className="ml-0.5 text-sm text-giver-low">/100</span>
            <p className="text-[10px] text-giver-low">final score</p>
          </div>
        </div>

        <p className="mt-4 text-sm leading-relaxed text-giver-slate">{article.neutral_summary}</p>
      </div>

      {/* Scores */}
      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <h3 className="mb-3 text-sm font-semibold text-giver-ink">Component scores</h3>
        <div className="space-y-2.5">
          <ScoreRow label="Importance" weight="35%" value={article.importance_score} />
          <ScoreRow label="Credibility" weight="30%" value={article.credibility_score} />
          <ScoreRow label="Relevance" weight="20%" value={article.relevance_score} />
          <ScoreRow label="Freshness" weight="10%" value={article.freshness_score} />
          <ScoreRow label="Src. Diversity" weight="5%" value={article.source_diversity_score} />
        </div>
      </section>

      {/* Framing */}
      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <h3 className="mb-2 text-sm font-semibold text-giver-ink">Framing assessment</h3>
        <span
          className={`inline-flex items-center rounded border px-2.5 py-1 text-sm font-medium ${framingStyle}`}
        >
          {framingText}
        </span>
      </section>

      {/* Key claims */}
      {article.key_claims.length > 0 && (
        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="mb-2 text-sm font-semibold text-giver-ink">Key claims</h3>
          <ul className="list-disc space-y-1 pl-5 text-sm text-giver-slate">
            {article.key_claims.map((claim, i) => (
              <li key={i}>{claim}</li>
            ))}
          </ul>
        </section>
      )}

      {/* Source support + contradictions */}
      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm space-y-3">
        <h3 className="text-sm font-semibold text-giver-ink">Source corroboration</h3>
        <p className="text-sm text-giver-slate">
          <span className="font-medium text-giver-ink">Support: </span>
          {article.support_summary}
        </p>
        {article.contradiction_warnings.length > 0 && (
          <div>
            <p className="text-sm font-medium text-giver-warn mb-1">Caution</p>
            <ul className="list-disc space-y-1 pl-5 text-sm text-giver-warn">
              {article.contradiction_warnings.map((w, i) => (
                <li key={i}>{w}</li>
              ))}
            </ul>
          </div>
        )}
      </section>

      {/* Why selected */}
      <section className="rounded-lg border border-slate-200 bg-giver-mist p-5">
        <h3 className="mb-1 text-sm font-semibold text-giver-ink">Why this article was selected</h3>
        <p className="text-sm text-giver-slate">{article.why_selected}</p>
      </section>

      {/* Bottom back link */}
      <Link href="/dashboard" className="inline-block text-sm text-giver-accent hover:underline">
        ← Back to Dashboard
      </Link>
    </div>
  );
}
