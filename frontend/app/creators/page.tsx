"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import CreatorDisclaimer from "@/components/CreatorDisclaimer";
import CreatorEmptyState from "@/components/CreatorEmptyState";
import ErrorState from "@/components/ErrorState";
import LoadingState from "@/components/LoadingState";
import { getCreators } from "@/lib/api";
import {
  CATEGORY_LABELS,
  CREATOR_LIST_INTRO,
  CREATOR_METRICS,
  scorePercent,
} from "@/lib/creatorDisplay";
import type { CreatorListItem } from "@/lib/types";

function ScorePill({
  label,
  value,
  help,
  variant = "neutral",
}: {
  label: string;
  value: number;
  help: string;
  variant?: "neutral" | "warn";
}) {
  const pct = scorePercent(value);
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
    <div className="flex flex-col items-center gap-1 text-center" title={help}>
      <span className={`text-lg font-bold tabular-nums ${textColor}`}>{pct}</span>
      <span className="text-[10px] font-medium text-giver-ink leading-tight">{label}</span>
      <span className="text-[9px] text-giver-low leading-snug line-clamp-2">{help}</span>
    </div>
  );
}

const CARD_METRICS = CREATOR_METRICS.filter((m) =>
  ["source_alignment_score", "claim_support_rate", "contradiction_rate"].includes(m.key),
);

function CreatorCard({ creator }: { creator: CreatorListItem }) {
  const metricValues: Record<string, number> = {
    source_alignment_score: creator.source_alignment_score,
    claim_support_rate: creator.claim_support_rate,
    contradiction_rate: creator.contradiction_rate,
  };

  return (
    <article className="rounded-lg border border-slate-200 bg-white shadow-sm hover:shadow-md transition-shadow">
      <div className="p-5 space-y-4">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="text-[10px] font-semibold uppercase tracking-wide text-giver-accent">
              Sample integrity profile
            </p>
            <h3 className="font-semibold text-giver-ink leading-snug mt-0.5">{creator.name}</h3>
            <p className="text-xs text-giver-low mt-0.5">
              {creator.handle} · {creator.platform}
            </p>
          </div>
          <span className="shrink-0 inline-flex items-center rounded border border-slate-200 bg-giver-mist px-2 py-0.5 text-[10px] font-medium text-giver-slate">
            {CATEGORY_LABELS[creator.category] ?? creator.category}
          </span>
        </div>

        <p className="text-sm text-giver-slate leading-relaxed line-clamp-3">{creator.bio}</p>

        <div className="rounded-md bg-giver-mist px-4 py-3 border border-slate-100">
          <p className="text-[10px] font-semibold uppercase tracking-wide text-giver-low mb-3">
            Information integrity signals · {creator.total_analyzed_posts} posts analyzed
          </p>
          <div className="grid grid-cols-3 gap-3">
            {CARD_METRICS.map((m) => (
              <ScorePill
                key={m.key}
                label={m.label.replace(" score", "").replace(" rate", "")}
                value={metricValues[m.key]}
                help={m.help}
                variant={m.variant}
              />
            ))}
          </div>
        </div>

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

        <div className="pt-1">
          <Link
            href={`/creators/${creator.creator_id}`}
            className="text-sm font-medium text-giver-accent hover:underline"
          >
            View sample integrity report →
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

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    getCreators()
      .then((res) => setCreators(res.creators))
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load creator profiles."))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-giver-ink">Creator Integrity Dashboard</h2>
        <p className="mt-1 text-sm text-giver-slate leading-relaxed">{CREATOR_LIST_INTRO}</p>
      </div>

      <CreatorDisclaimer compact />

      <details className="group rounded-lg border border-slate-200 bg-giver-mist">
        <summary className="flex cursor-pointer select-none items-center justify-between px-4 py-3 text-sm font-medium text-giver-ink">
          <span>What these metrics mean</span>
          <span className="text-giver-low transition-transform group-open:rotate-180">▾</span>
        </summary>
        <div className="border-t border-slate-200 px-4 py-3 space-y-3">
          {CREATOR_METRICS.map((m) => (
            <div key={m.key} className="text-xs">
              <p className="font-medium text-giver-ink">{m.label}</p>
              <p className="text-giver-slate mt-0.5 leading-relaxed">{m.help}</p>
            </div>
          ))}
          <p className="text-[11px] text-giver-low pt-1 border-t border-slate-200">
            Metrics are derived from analyzed post content via the information-integrity engine.
            Analyses persist in SQLite until content changes. Demo posts:{" "}
            <code className="rounded bg-white px-1">POST /v1/creators/&#123;id&#125;/posts/demo</code>{" "}
            (see <code className="rounded bg-white px-1">docs/CREATOR_DEMO_WORKFLOW.md</code>).
          </p>
        </div>
      </details>

      {loading && (
        <LoadingState
          title="Loading creator profiles…"
          subtitle="Preparing sample integrity summaries from analyzed posts."
        />
      )}

      {error && (
        <ErrorState
          message={error}
          onRetry={load}
        />
      )}

      {!loading && !error && creators.length === 0 && (
        <CreatorEmptyState
          title="No creator profiles yet"
          description="Creator fixtures are not available. Check that the backend is running and creator data is configured."
        />
      )}

      {!loading && !error && creators.length > 0 && (
        <>
          <p className="text-xs font-medium text-giver-low uppercase tracking-wide">
            {creators.length} sample profile{creators.length !== 1 ? "s" : ""} · derived from analyzed posts
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
