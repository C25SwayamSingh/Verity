"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import CreatorDisclaimer from "@/components/CreatorDisclaimer";
import CreatorEmptyState from "@/components/CreatorEmptyState";
import CreatorMetricBar from "@/components/CreatorMetricBar";
import ErrorState from "@/components/ErrorState";
import LoadingState from "@/components/LoadingState";
import { getCreator, getCreatorPosts } from "@/lib/api";
import {
  CATEGORY_LABELS,
  CORROBORATION_LABELS,
  CORROBORATION_STYLES,
  CREATOR_METRICS,
  FRAMING_LABELS,
  FRAMING_STYLES,
  formatCreatorDate,
  scorePercent,
} from "@/lib/creatorDisplay";
import type { CreatorOverview, CreatorPost, WeakClaim } from "@/lib/types";

function GlanceStat({
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
  const color =
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
    <div className="rounded-lg border border-slate-200 bg-white p-4 text-center">
      <p className={`text-2xl font-bold tabular-nums ${color}`}>{pct}</p>
      <p className="text-xs font-medium text-giver-ink mt-1">{label}</p>
      <p className="text-[10px] text-giver-low mt-1 leading-snug">{help}</p>
    </div>
  );
}

function WeakestClaimCard({ claim }: { claim: WeakClaim }) {
  const cs =
    CORROBORATION_STYLES[claim.corroboration_status] ??
    "bg-slate-50 text-slate-600 border-slate-200";
  const cl =
    CORROBORATION_LABELS[claim.corroboration_status] ?? claim.corroboration_status;

  return (
    <div className="rounded-md border border-amber-100 bg-amber-50/40 px-4 py-3 space-y-2">
      <p className="text-sm text-giver-ink leading-snug">
        <span className="text-giver-low text-xs font-medium uppercase tracking-wide block mb-1">
          Claim
        </span>
        &ldquo;{claim.text}&rdquo;
      </p>
      <div className="flex flex-wrap items-center gap-2">
        <span
          className={`inline-flex items-center rounded border px-2 py-0.5 text-xs font-medium ${cs}`}
        >
          {cl}
        </span>
        <span className="text-[10px] text-giver-low">Post ref: {claim.post_id}</span>
      </div>
      {claim.note && (
        <p className="text-xs text-giver-slate border-t border-amber-100/80 pt-2 leading-relaxed">
          <span className="font-medium text-giver-ink">What we observed: </span>
          {claim.note}
        </p>
      )}
    </div>
  );
}

function PostCard({ post }: { post: CreatorPost }) {
  const [expanded, setExpanded] = useState(false);
  const framingStyle =
    FRAMING_STYLES[post.framing_label] ?? "bg-slate-50 text-slate-600 border-slate-200";
  const framingText = FRAMING_LABELS[post.framing_label] ?? post.framing_label;
  const alignPct = scorePercent(post.source_alignment_score);
  const alignColor =
    alignPct >= 75 ? "text-giver-ok" : alignPct >= 55 ? "text-giver-accent" : "text-giver-warn";

  return (
    <div className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="p-4 space-y-3">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <h4 className="text-sm font-semibold text-giver-ink leading-snug">{post.title}</h4>
            <p className="text-xs text-giver-low mt-0.5">
              {post.platform} · {post.topic} · {formatCreatorDate(post.published_at)}
            </p>
          </div>
          <div className="shrink-0 text-right">
            <span className={`text-xl font-bold tabular-nums ${alignColor}`}>{alignPct}</span>
            <p className="text-[10px] text-giver-low">source alignment</p>
          </div>
        </div>

        <p className="text-sm text-giver-slate leading-relaxed">{post.summary}</p>

        {post.input_basis_note && (
          <p className="text-xs text-amber-900 bg-amber-50 border border-amber-200 rounded-md px-3 py-2 leading-relaxed">
            {post.input_basis_note}
          </p>
        )}
        {post.input_basis_label && !post.input_basis_note && (
          <p className="text-xs text-giver-low">
            Input basis: {post.input_basis_label}
          </p>
        )}

        <div className="flex flex-wrap items-center gap-2">
          <span
            className={`inline-flex items-center rounded border px-2 py-0.5 text-xs font-medium ${framingStyle}`}
          >
            Framing: {framingText}
          </span>
          {post.claims.length > 0 && (
            <span className="text-xs text-giver-slate">
              {post.claims.length} claim{post.claims.length !== 1 ? "s" : ""}
              {post.supported_claims_count > 0 && (
                <span className="text-giver-ok ml-1">
                  · {post.supported_claims_count} with claim support
                </span>
              )}
              {post.contradicted_claims_count > 0 && (
                <span className="text-giver-warn ml-1">
                  · {post.contradicted_claims_count} contradiction signal
                  {post.contradicted_claims_count !== 1 ? "s" : ""}
                </span>
              )}
              {post.low_corroboration_claims_count > 0 && (
                <span className="text-amber-700 ml-1">
                  · {post.low_corroboration_claims_count} low corroboration
                </span>
              )}
            </span>
          )}
        </div>

        {post.claims.length > 0 && (
          <div>
            <button
              type="button"
              onClick={() => setExpanded((v) => !v)}
              className="text-xs font-medium text-giver-accent hover:underline"
            >
              {expanded ? "Hide claim breakdown ▴" : "View claim breakdown ▾"}
            </button>
            {expanded && (
              <ul className="mt-2 space-y-2">
                {post.claims.map((claim) => {
                  const cs =
                    CORROBORATION_STYLES[claim.corroboration_status] ??
                    "bg-slate-50 text-slate-600 border-slate-200";
                  const cl =
                    CORROBORATION_LABELS[claim.corroboration_status] ??
                    claim.corroboration_status;
                  return (
                    <li
                      key={claim.claim_id}
                      className="rounded border border-slate-100 bg-giver-mist px-3 py-2 space-y-1.5"
                    >
                      <p className="text-xs text-giver-ink leading-snug">{claim.text}</p>
                      <div className="flex flex-wrap gap-1.5 items-center">
                        <span
                          className={`inline-flex items-center rounded border px-1.5 py-0.5 text-[10px] font-medium ${cs}`}
                        >
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

        {post.sources_used.length > 0 && (
          <div>
            <p className="text-[10px] font-medium text-giver-low uppercase tracking-wide mb-1">
              Sources referenced
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

export default function CreatorDetailPage() {
  const params = useParams();
  const id = typeof params.id === "string" ? params.id : "";

  const [creator, setCreator] = useState<CreatorOverview | null>(null);
  const [posts, setPosts] = useState<CreatorPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    if (!id) return;
    setLoading(true);
    setError(null);
    Promise.all([getCreator(id), getCreatorPosts(id)])
      .then(([c, p]) => {
        setCreator(c);
        setPosts(p.posts);
      })
      .catch((e) =>
        setError(
          e instanceof Error ? e.message : "Could not load this integrity report.",
        ),
      )
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  if (!id) {
    return (
      <div className="space-y-4">
        <Link href="/creators" className="text-sm text-giver-accent hover:underline">
          ← Back to Creators
        </Link>
        <ErrorState message="Invalid creator link." />
      </div>
    );
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <Link href="/creators" className="text-sm text-giver-accent hover:underline">
          ← Back to Creators
        </Link>
        <LoadingState
          title="Building integrity report…"
          subtitle="Loading cross-source corroboration, claim support, and framing indicators for this creator."
        />
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <Link href="/creators" className="text-sm text-giver-accent hover:underline">
          ← Back to Creators
        </Link>
        <ErrorState message={error} onRetry={load} />
      </div>
    );
  }

  if (!creator) return null;

  const alignPct = scorePercent(creator.source_alignment_score);
  const alignColor =
    alignPct >= 75 ? "text-giver-ok" : alignPct >= 55 ? "text-giver-accent" : "text-giver-warn";

  const metricValues: Record<string, number> = {
    source_alignment_score: creator.source_alignment_score,
    claim_support_rate: creator.claim_support_rate,
    contradiction_rate: creator.contradiction_rate,
    low_corroboration_rate: creator.low_corroboration_rate,
    source_diversity_score: creator.source_diversity_score,
    average_framing_score: creator.average_framing_score,
  };

  return (
    <div className="space-y-6">
      <Link href="/creators" className="inline-block text-sm text-giver-accent hover:underline">
        ← Back to Creators
      </Link>

      <CreatorDisclaimer />

      {/* Report header */}
      <header className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm border-t-4 border-t-giver-accent">
        <p className="text-[10px] font-semibold uppercase tracking-wide text-giver-accent mb-2">
          Sample information integrity report
        </p>
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0 flex-1">
            <h1 className="text-xl font-semibold text-giver-ink">{creator.name}</h1>
            <p className="text-sm text-giver-low mt-1">
              {creator.handle} · {creator.platform} ·{" "}
              {CATEGORY_LABELS[creator.category] ?? creator.category}
            </p>
          </div>
          <div className="shrink-0 text-right rounded-lg bg-giver-mist px-3 py-2">
            <span className={`text-3xl font-bold tabular-nums ${alignColor}`}>{alignPct}</span>
            <span className="ml-0.5 text-sm text-giver-low">/100</span>
            <p className="text-[10px] font-medium text-giver-ink mt-0.5">Source alignment</p>
            <p className="text-[9px] text-giver-low max-w-[8rem] leading-snug">
              Overall alignment with cross-referenced sources
            </p>
          </div>
        </div>
        <p className="mt-4 text-sm leading-relaxed text-giver-slate">{creator.bio}</p>
        <p className="mt-3 text-xs text-giver-low">
          Based on {creator.total_analyzed_posts} analyzed post
          {creator.total_analyzed_posts !== 1 ? "s" : ""}
          {creator.metrics_source === "derived_from_analysis" && (
            <span> · signals derived from the integrity engine</span>
          )}
        </p>
      </header>

      {/* At a glance */}
      <section>
        <h2 className="text-sm font-semibold text-giver-ink mb-1">At a glance</h2>
        <p className="text-xs text-giver-low mb-3">
          Key information integrity signals across this creator&apos;s analyzed content.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <GlanceStat
            label="Claim support"
            value={creator.claim_support_rate}
            help="Claims with medium or high corroboration"
            variant="neutral"
          />
          <GlanceStat
            label="Contradiction signals"
            value={creator.contradiction_rate}
            help="Claims with cross-source contradiction"
            variant="warn"
          />
          <GlanceStat
            label="Low corroboration"
            value={creator.low_corroboration_rate}
            help="Claims with limited source support"
            variant="warn"
          />
        </div>
      </section>

      {/* Full metrics */}
      <section className="rounded-lg border border-slate-200 bg-giver-mist/50 p-5 shadow-sm">
        <h2 className="text-sm font-semibold text-giver-ink mb-1">Information integrity signals</h2>
        <p className="text-xs text-giver-low mb-4">
          Each metric includes a short explanation. Scores reflect analyzed posts only.
        </p>
        <div className="space-y-2">
          {CREATOR_METRICS.map((m) => (
            <CreatorMetricBar
              key={m.key}
              label={m.label}
              value={metricValues[m.key]}
              help={m.help}
              variant={m.variant}
            />
          ))}
        </div>
      </section>

      {/* Transparency summary */}
      <section
        className="rounded-lg border border-giver-accent/20 bg-gradient-to-br from-giver-mist to-white p-5 shadow-sm"
        aria-labelledby="transparency-heading"
      >
        <h2 id="transparency-heading" className="text-sm font-semibold text-giver-ink mb-1">
          Transparency summary
        </h2>
        <p className="text-xs text-giver-low mb-3">
          A plain-language overview of source alignment and claim patterns for this sample report.
        </p>
        <p className="text-sm leading-relaxed text-giver-slate">{creator.transparency_summary}</p>
      </section>

      <div className="grid gap-4 sm:grid-cols-2">
        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-sm font-semibold text-giver-ink mb-1">Top topics</h2>
          <p className="text-xs text-giver-low mb-3">Recurring subject areas in analyzed posts.</p>
          {creator.top_topics.length > 0 ? (
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
          ) : (
            <p className="text-sm text-giver-slate">No topics identified yet.</p>
          )}
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-sm font-semibold text-giver-ink mb-1">Most used sources</h2>
          <p className="text-xs text-giver-low mb-3">
            Publishers most often referenced for cross-source corroboration.
          </p>
          {creator.most_used_sources.length > 0 ? (
            <ul className="space-y-1.5">
              {creator.most_used_sources.map((src) => (
                <li key={src} className="text-sm text-giver-slate flex items-start gap-2">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-giver-accent" />
                  {src}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-giver-slate">No supporting sources recorded yet.</p>
          )}
        </section>
      </div>

      {creator.most_reliable_posts.length > 0 && (
        <section className="rounded-lg border border-emerald-100 bg-emerald-50/30 px-4 py-3">
          <h2 className="text-xs font-semibold text-giver-ink">Strongest source alignment (posts)</h2>
          <p className="text-xs text-giver-slate mt-1">
            Post IDs with the highest source alignment in this sample:{" "}
            <span className="font-medium text-giver-ink">
              {creator.most_reliable_posts.join(", ")}
            </span>
          </p>
        </section>
      )}

      {creator.weakest_claims.length > 0 ? (
        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-sm font-semibold text-giver-ink mb-1">Claims needing attention</h2>
          <p className="text-xs text-giver-low mb-4 leading-relaxed">
            Statements with low corroboration or contradiction signals. These are observation
            notes for source transparency—not accusations about the creator.
          </p>
          <div className="space-y-3">
            {creator.weakest_claims.map((wc) => (
              <WeakestClaimCard key={wc.claim_id} claim={wc} />
            ))}
          </div>
        </section>
      ) : (
        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-sm font-semibold text-giver-ink mb-1">Claims needing attention</h2>
          <p className="text-sm text-giver-slate mt-2">
            No low-corroboration or contradiction signals were flagged in this sample.
          </p>
        </section>
      )}

      <section className="space-y-3">
        <div>
          <h2 className="text-sm font-semibold text-giver-ink">
            Analyzed posts ({posts.length})
          </h2>
          <p className="text-xs text-giver-low mt-1">
            Per-post summaries with framing indicators and claim-level corroboration.
          </p>
        </div>
        {posts.length > 0 ? (
          posts.map((post) => <PostCard key={post.post_id} post={post} />)
        ) : (
          <CreatorEmptyState
            title="No analyzed posts for this creator"
            description="Add demo transcript or article text via the internal demo form to build a sample report."
            actionHref={`/creators/demo?creator_id=${creator.creator_id}`}
            actionLabel="Add demo post"
          />
        )}
      </section>

      <footer className="pt-2 border-t border-slate-200 space-y-3">
        <CreatorDisclaimer compact />
        <p className="text-xs text-giver-low">
          Internal demo:{" "}
          <Link
            href={`/creators/demo?creator_id=${creator.creator_id}`}
            className="text-giver-accent hover:underline"
          >
            Add demo post for this profile
          </Link>
        </p>
        <Link
          href="/creators"
          className="inline-block text-sm text-giver-accent hover:underline"
        >
          ← Back to all creator profiles
        </Link>
      </footer>
    </div>
  );
}
