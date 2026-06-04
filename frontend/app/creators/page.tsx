"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import ErrorState from "@/components/ErrorState";
import LoadingState from "@/components/LoadingState";
import { getCreators } from "@/lib/api";
import type { CreatorListItem } from "@/lib/types";

const FRAMING_STYLES: Record<string, string> = {
  mostly_neutral: "bg-emerald-50 text-emerald-700 border-emerald-200",
  mixed_framing: "bg-amber-50 text-amber-700 border-amber-200",
  notable_framing: "bg-red-50 text-red-700 border-red-200",
};

const CATEGORY_LABELS: Record<string, string> = {
  breaking: "Breaking",
  domestic_us: "Domestic / U.S.",
  foreign_world: "Foreign / World",
  markets_stocks: "Markets / Stocks",
  tech_ai: "Tech & AI",
  other: "Other",
};

function ScorePill({
  label,
  value,
  variant = "neutral",
}: {
  label: string;
  value: number;
  variant?: "neutral" | "warn";
}) {
  const pct = Math.round(value * 100);
  const textColor =
    variant === "warn"
      ? pct <= 15
        ? "text-giver-ok"
        : pct <= 30
          ? "text-amber-700"
          : "text-giver-warn"
      : pct >= 75
        ? "text-giver-ok"
        : pct >= 55
          ? "text-giver-accent"
          : "text-giver-warn";

  return (
    <div className="flex flex-col items-center gap-0.5">
      <span className={`text-lg font-bold tabular-nums ${textColor}`}>{pct}</span>
      <span className="text-[10px] text-giver-low text-center leading-tight">{label}</span>
    </div>
  );
}

function CreatorCard({ creator }: { creator: CreatorListItem }) {
  return (
    <article className="rounded-lg border border-slate-200 bg-white shadow-sm hover:shadow-md transition-shadow">
      <div className="p-5 space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <h3 className="font-semibold text-giver-ink leading-snug">{creator.name}</h3>
            <p className="text-xs text-giver-low mt-0.5">
              {creator.handle} · {creator.platform}
            </p>
          </div>
          <span className="shrink-0 inline-flex items-center rounded border border-slate-200 bg-giver-mist px-2 py-0.5 text-[10px] font-medium text-giver-slate">
            {CATEGORY_LABELS[creator.category] ?? creator.category}
          </span>
        </div>

        {/* Bio */}
        <p className="text-sm text-giver-slate leading-relaxed line-clamp-3">{creator.bio}</p>

        {/* Integrity metrics */}
        <div className="rounded-md bg-giver-mist px-4 py-3">
          <p className="text-[10px] font-semibold uppercase tracking-wide text-giver-low mb-3">
            Integrity metrics · {creator.total_analyzed_posts} posts analyzed
          </p>
          <div className="grid grid-cols-3 gap-3 text-center">
            <ScorePill
              label="Source alignment"
              value={creator.source_alignment_score}
              variant="neutral"
            />
            <ScorePill
              label="Claim support rate"
              value={creator.claim_support_rate}
              variant="neutral"
            />
            <ScorePill
              label="Contradiction rate"
              value={creator.contradiction_rate}
              variant="warn"
            />
          </div>
        </div>

        {/* Top topics */}
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-wide text-giver-low mb-1.5">
            Top topics
          </p>
          <div className="flex flex-wrap gap-1.5">
            {creator.top_topics.slice(0, 4).map((topic) => (
              <span
                key={topic}
                className="inline-flex items-center rounded-full border border-slate-200 bg-white px-2.5 py-0.5 text-xs text-giver-slate"
              >
                {topic}
              </span>
            ))}
          </div>
        </div>

        {/* Link */}
        <div className="pt-1">
          <Link
            href={`/creators/${creator.creator_id}`}
            className="text-sm font-medium text-giver-accent hover:underline"
          >
            View integrity profile →
          </Link>
        </div>
      </div>
    </article>
  );
}

export default function CreatorsPage() {
  const [creators, setCreators] = useState<CreatorListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getCreators()
      .then((res) => setCreators(res.creators))
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load creators."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">

      {/* Page header */}
      <div>
        <h2 className="text-lg font-semibold text-giver-ink">
          Creator Integrity Dashboard
        </h2>
        <p className="mt-1 text-sm text-giver-slate">
          An overview of how information-focused creators&apos; posts perform across source
          alignment, claim support, contradiction rate, framing profile, and source diversity.
          Creator metrics are derived from analyzed fixture post content via the core
          integrity engine — no social media APIs are connected.
        </p>
      </div>

      {/* Methodology disclosure */}
      <details className="group rounded-lg border border-slate-200 bg-giver-mist">
        <summary className="flex cursor-pointer select-none items-center justify-between px-4 py-3 text-sm font-medium text-giver-ink">
          <span>Methodology — how creator metrics are calculated</span>
          <span className="text-giver-low transition-transform group-open:rotate-180">▾</span>
        </summary>
        <div className="border-t border-slate-200 px-4 py-3 text-xs text-giver-slate space-y-2">
          <p>
            Each creator&apos;s integrity profile is derived from the analyzed posts attributed to them.
            No verdicts about truthfulness are issued. Metrics use neutral language:
          </p>
          <table className="w-full text-xs">
            <thead>
              <tr className="text-left text-giver-low">
                <th className="pb-1 font-medium">Metric</th>
                <th className="pb-1 pl-4 font-medium">What it measures</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {[
                ["Source alignment score", "Share of claims that align with cited or cross-referenced sources"],
                ["Claim support rate", "Proportion of claims with medium or high corroboration across analyzed posts"],
                ["Contradiction rate", "Proportion of claims contradicted by cross-source evidence"],
                ["Low corroboration rate", "Proportion of claims lacking adequate supporting sources"],
                ["Source diversity score", "Range and independence of sources referenced across posts"],
                ["Average framing score", "Composite framing neutrality across analyzed posts (higher = more neutral)"],
              ].map(([metric, desc]) => (
                <tr key={metric} className="align-top">
                  <td className="py-1 font-medium text-giver-ink whitespace-nowrap pr-4">{metric}</td>
                  <td className="py-1 text-giver-slate">{desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="text-giver-low">
            Scores are computed from claim corroboration, framing, and source signals produced by
            running each fixture post through the analysis pipeline (deterministic path; no API key required).
          </p>
        </div>
      </details>

      {/* Content */}
      {loading && <LoadingState />}
      {error && <ErrorState message={error} />}

      {!loading && !error && creators.length === 0 && (
        <p className="text-sm text-giver-slate">No creator profiles available.</p>
      )}

      {!loading && !error && creators.length > 0 && (
        <>
          <p className="text-xs font-medium text-giver-low uppercase tracking-wide">
            {creators.length} creator{creators.length !== 1 ? "s" : ""} · derived from analyzed posts
          </p>
          <div className="grid gap-4 sm:grid-cols-2">
            {creators.map((creator) => (
              <CreatorCard key={creator.creator_id} creator={creator} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
