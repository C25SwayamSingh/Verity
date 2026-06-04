"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import ErrorState from "@/components/ErrorState";
import LoadingState from "@/components/LoadingState";
import { getCreator, getCreatorPosts } from "@/lib/api";
import type { CreatorOverview, CreatorPost } from "@/lib/types";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

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

const CORROBORATION_STYLES: Record<string, string> = {
  high_corroboration: "bg-emerald-50 text-emerald-700 border-emerald-200",
  medium_corroboration: "bg-blue-50 text-blue-700 border-blue-200",
  low_corroboration: "bg-amber-50 text-amber-700 border-amber-200",
  contradicted: "bg-red-50 text-red-700 border-red-200",
  not_checkable: "bg-slate-50 text-slate-500 border-slate-200",
};

const CORROBORATION_LABELS: Record<string, string> = {
  high_corroboration: "High corroboration",
  medium_corroboration: "Medium corroboration",
  low_corroboration: "Low corroboration",
  contradicted: "Contradicted",
  not_checkable: "Not checkable",
};

const CATEGORY_LABELS: Record<string, string> = {
  breaking: "Breaking",
  domestic_us: "Domestic / U.S.",
  foreign_world: "Foreign / World",
  markets_stocks: "Markets / Stocks",
  tech_ai: "Tech & AI",
  other: "Other",
};

// ---------------------------------------------------------------------------
// Small shared components
// ---------------------------------------------------------------------------

function MetricBar({
  label,
  value,
  variant = "neutral",
}: {
  label: string;
  value: number;
  variant?: "neutral" | "warn";
}) {
  const pct = Math.round(value * 100);
  let barColor: string;
  let textColor: string;

  if (variant === "warn") {
    barColor = pct <= 15 ? "bg-giver-ok" : pct <= 30 ? "bg-amber-500" : "bg-giver-warn";
    textColor = pct <= 15 ? "text-giver-ok" : pct <= 30 ? "text-amber-700" : "text-giver-warn";
  } else {
    barColor = pct >= 75 ? "bg-giver-ok" : pct >= 55 ? "bg-giver-accent" : "bg-giver-warn";
    textColor = pct >= 75 ? "text-giver-ok" : pct >= 55 ? "text-giver-accent" : "text-giver-warn";
  }

  return (
    <div className="flex items-center gap-3">
      <div className="w-44 shrink-0 text-xs font-medium text-giver-ink">{label}</div>
      <div className="flex-1 h-2 rounded-full bg-slate-200">
        <div className={`h-2 rounded-full ${barColor}`} style={{ width: `${pct}%` }} />
      </div>
      <span className={`w-8 shrink-0 text-right text-xs font-semibold tabular-nums ${textColor}`}>
        {pct}
      </span>
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

// ---------------------------------------------------------------------------
// Post card
// ---------------------------------------------------------------------------

function PostCard({ post }: { post: CreatorPost }) {
  const [expanded, setExpanded] = useState(false);
  const framingStyle = FRAMING_STYLES[post.framing_label] ?? "bg-slate-50 text-slate-600 border-slate-200";
  const framingText = FRAMING_LABELS[post.framing_label] ?? post.framing_label;
  const alignPct = Math.round(post.source_alignment_score * 100);
  const alignColor =
    alignPct >= 75 ? "text-giver-ok" : alignPct >= 55 ? "text-giver-accent" : "text-giver-warn";

  const totalClaims = post.claims.length;

  return (
    <div className="rounded-lg border border-slate-200 bg-white">
      <div className="p-4 space-y-3">
        {/* Post header */}
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <h4 className="text-sm font-semibold text-giver-ink leading-snug">{post.title}</h4>
            <p className="text-xs text-giver-low mt-0.5">
              {post.platform} · {post.topic} · {formatDate(post.published_at)}
            </p>
          </div>
          <div className="shrink-0 text-right">
            <span className={`text-xl font-bold tabular-nums ${alignColor}`}>{alignPct}</span>
            <p className="text-[10px] text-giver-low">alignment</p>
          </div>
        </div>

        {/* Summary */}
        <p className="text-sm text-giver-slate leading-relaxed">{post.summary}</p>

        {/* Stats row */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Framing badge */}
          <span
            className={`inline-flex items-center rounded border px-2 py-0.5 text-xs font-medium ${framingStyle}`}
          >
            {framingText}
          </span>

          {/* Claim counts */}
          {totalClaims > 0 && (
            <span className="text-xs text-giver-slate">
              <span className="font-medium">{totalClaims}</span> claim{totalClaims !== 1 ? "s" : ""}
              {post.supported_claims_count > 0 && (
                <span className="text-giver-ok ml-1">· {post.supported_claims_count} supported</span>
              )}
              {post.contradicted_claims_count > 0 && (
                <span className="text-giver-warn ml-1">· {post.contradicted_claims_count} contradicted</span>
              )}
              {post.low_corroboration_claims_count > 0 && (
                <span className="text-amber-700 ml-1">· {post.low_corroboration_claims_count} low corroboration</span>
              )}
            </span>
          )}
        </div>

        {/* Expandable claims */}
        {post.claims.length > 0 && (
          <div>
            <button
              onClick={() => setExpanded((v) => !v)}
              className="text-xs font-medium text-giver-accent hover:underline"
            >
              {expanded ? "Hide claims ▴" : "Show claims ▾"}
            </button>
            {expanded && (
              <ul className="mt-2 space-y-2">
                {post.claims.map((claim) => {
                  const cs = CORROBORATION_STYLES[claim.corroboration_status] ?? "bg-slate-50 text-slate-600 border-slate-200";
                  const cl = CORROBORATION_LABELS[claim.corroboration_status] ?? claim.corroboration_status;
                  return (
                    <li key={claim.claim_id} className="rounded border border-slate-100 bg-giver-mist px-3 py-2 space-y-1">
                      <p className="text-xs text-giver-ink">{claim.text}</p>
                      <div className="flex flex-wrap gap-1.5 items-center">
                        <span className={`inline-flex items-center rounded border px-1.5 py-0.5 text-[10px] font-medium ${cs}`}>
                          {cl}
                        </span>
                        <span className="text-[10px] text-giver-low capitalize">
                          {claim.claim_type.replace(/_/g, " ")}
                        </span>
                      </div>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        )}

        {/* Sources used */}
        {post.sources_used.length > 0 && (
          <div>
            <p className="text-[10px] font-medium text-giver-low uppercase tracking-wide mb-1">
              Sources cited
            </p>
            <div className="flex flex-wrap gap-1.5">
              {post.sources_used.map((src) => (
                <span
                  key={src}
                  className="inline-flex items-center rounded-full border border-slate-200 bg-white px-2.5 py-0.5 text-xs text-giver-slate"
                >
                  {src}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------

export default function CreatorDetailPage() {
  const params = useParams();
  const id = typeof params.id === "string" ? params.id : "";

  const [creator, setCreator] = useState<CreatorOverview | null>(null);
  const [posts, setPosts] = useState<CreatorPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    Promise.all([getCreator(id), getCreatorPosts(id)])
      .then(([c, p]) => {
        setCreator(c);
        setPosts(p.posts);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Creator not found."))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <LoadingState />;
  if (error) {
    return (
      <div className="space-y-4">
        <Link href="/creators" className="text-sm text-giver-accent hover:underline">
          ← Back to Creators
        </Link>
        <ErrorState message={error} />
      </div>
    );
  }
  if (!creator) return null;

  const alignPct = Math.round(creator.source_alignment_score * 100);
  const alignColor =
    alignPct >= 75 ? "text-giver-ok" : alignPct >= 55 ? "text-giver-accent" : "text-giver-warn";

  return (
    <div className="space-y-6">

      {/* Back nav */}
      <Link href="/creators" className="inline-block text-sm text-giver-accent hover:underline">
        ← Back to Creators
      </Link>

      {/* Header card */}
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0 flex-1">
            <h2 className="text-lg font-semibold text-giver-ink">{creator.name}</h2>
            <p className="text-sm text-giver-low mt-0.5">
              {creator.handle} · {creator.platform} ·{" "}
              {CATEGORY_LABELS[creator.category] ?? creator.category}
            </p>
          </div>
          <div className="shrink-0 text-right">
            <span className={`text-3xl font-bold tabular-nums ${alignColor}`}>{alignPct}</span>
            <span className="ml-0.5 text-sm text-giver-low">/100</span>
            <p className="text-[10px] text-giver-low">source alignment</p>
          </div>
        </div>
        <p className="mt-4 text-sm leading-relaxed text-giver-slate">{creator.bio}</p>
        <p className="mt-2 text-xs text-giver-low">
          {creator.total_analyzed_posts} post{creator.total_analyzed_posts !== 1 ? "s" : ""} analyzed
          {creator.metrics_source === "derived_from_analysis" && (
            <span> · metrics derived from analyzed posts</span>
          )}
        </p>
      </div>

      {/* Integrity metrics */}
      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <h3 className="mb-4 text-sm font-semibold text-giver-ink">Integrity metrics</h3>
        <div className="space-y-2.5">
          <MetricBar label="Source alignment" value={creator.source_alignment_score} />
          <MetricBar label="Claim support rate" value={creator.claim_support_rate} />
          <MetricBar label="Contradiction rate" value={creator.contradiction_rate} variant="warn" />
          <MetricBar label="Low corroboration rate" value={creator.low_corroboration_rate} variant="warn" />
          <MetricBar label="Source diversity" value={creator.source_diversity_score} />
          <MetricBar label="Average framing score" value={creator.average_framing_score} />
        </div>
        <p className="mt-3 text-[10px] text-giver-low">
          Higher is better for alignment, support rate, diversity, and framing score.
          Lower is better for contradiction and low-corroboration rates.
        </p>
      </section>

      {/* Transparency summary */}
      <section className="rounded-lg border border-slate-200 bg-giver-mist p-5">
        <h3 className="mb-2 text-sm font-semibold text-giver-ink">Transparency summary</h3>
        <p className="text-sm leading-relaxed text-giver-slate">{creator.transparency_summary}</p>
      </section>

      {/* Top topics + most used sources */}
      <div className="grid gap-4 sm:grid-cols-2">
        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="mb-3 text-sm font-semibold text-giver-ink">Top topics</h3>
          <div className="flex flex-wrap gap-2">
            {creator.top_topics.map((topic) => (
              <span
                key={topic}
                className="inline-flex items-center rounded-full border border-slate-200 bg-giver-mist px-3 py-1 text-xs text-giver-slate"
              >
                {topic}
              </span>
            ))}
          </div>
        </section>
        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="mb-3 text-sm font-semibold text-giver-ink">Most used sources</h3>
          <ul className="space-y-1">
            {creator.most_used_sources.map((src) => (
              <li key={src} className="text-sm text-giver-slate flex items-start gap-1.5">
                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-giver-accent" />
                {src}
              </li>
            ))}
          </ul>
        </section>
      </div>

      {/* Weakest claims */}
      {creator.weakest_claims.length > 0 && (
        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="mb-1 text-sm font-semibold text-giver-ink">Weakest claims</h3>
          <p className="text-xs text-giver-low mb-3">
            Claims that received low corroboration or were contradicted by cross-source evidence.
          </p>
          <div className="space-y-3">
            {creator.weakest_claims.map((wc) => {
              const cs = CORROBORATION_STYLES[wc.corroboration_status] ?? "bg-slate-50 text-slate-600 border-slate-200";
              const cl = CORROBORATION_LABELS[wc.corroboration_status] ?? wc.corroboration_status;
              return (
                <div key={wc.claim_id} className="rounded-md border border-slate-100 bg-giver-mist px-4 py-3 space-y-1.5">
                  <p className="text-sm text-giver-ink leading-snug">&ldquo;{wc.text}&rdquo;</p>
                  <div className="flex flex-wrap gap-2 items-center">
                    <span className={`inline-flex items-center rounded border px-2 py-0.5 text-xs font-medium ${cs}`}>
                      {cl}
                    </span>
                  </div>
                  <p className="text-xs text-giver-slate">{wc.note}</p>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* Analyzed posts */}
      {posts.length > 0 && (
        <section className="space-y-3">
          <h3 className="text-sm font-semibold text-giver-ink">
            Analyzed posts ({posts.length})
          </h3>
          {posts.map((post) => (
            <PostCard key={post.post_id} post={post} />
          ))}
        </section>
      )}

      {/* Bottom back link */}
      <Link href="/creators" className="inline-block text-sm text-giver-accent hover:underline">
        ← Back to Creators
      </Link>
    </div>
  );
}
