"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import ErrorState from "@/components/ErrorState";
import LoadingState from "@/components/LoadingState";
import NewsFeedCard from "@/components/NewsFeedCard";
import { getNewsFeed } from "@/lib/api";
import type { DashboardCategory, NewsFeedItem, NewsFeedResponse } from "@/lib/types";

const CATEGORIES: { value: DashboardCategory; label: string }[] = [
  { value: "breaking", label: "Breaking" },
  { value: "domestic_us", label: "Domestic / U.S." },
  { value: "foreign_world", label: "Foreign / World" },
  { value: "markets_stocks", label: "Markets / Stocks" },
  { value: "tech_ai", label: "Tech & AI" },
];

export default function HomePage() {
  const [category, setCategory] = useState<DashboardCategory>("breaking");
  const [feed, setFeed] = useState<NewsFeedResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [index, setIndex] = useState(0);
  const [saved, setSaved] = useState<NewsFeedItem[]>([]);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    setFeed(null);
    setIndex(0);

    getNewsFeed(category)
      .then((res) => {
        if (!cancelled) setFeed(res);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load the feed.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [category]);

  const items = feed?.items ?? [];
  const current = items[index];
  const atEnd = !loading && !error && items.length > 0 && index >= items.length;

  const savedIds = useMemo(() => new Set(saved.map((s) => s.id)), [saved]);

  function advance() {
    setIndex((i) => Math.min(i + 1, items.length));
  }

  function handleSave() {
    if (current && !savedIds.has(current.id)) {
      setSaved((s) => [...s, current]);
    }
    advance();
  }

  function restart() {
    setIndex(0);
  }

  return (
    <div className="space-y-6">
      {/* Hero */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-giver-ink">News Integrity Feed</h2>
          <p className="mt-1 max-w-xl text-sm text-giver-slate">
            Browse today&rsquo;s stories and quickly see how consistently each one is reported:
            cross-source corroboration, contradiction signals, framing indicators, and a neutral
            summary. Signals are based on available source overlap, not absolute truth.
          </p>
        </div>
        <Link
          href="/check"
          className="inline-flex shrink-0 items-center justify-center rounded-md bg-giver-accent px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700"
        >
          Check your own →
        </Link>
      </div>

      {/* Category filter */}
      <div className="flex flex-wrap gap-2">
        {CATEGORIES.map((c) => {
          const active = c.value === category;
          return (
            <button
              key={c.value}
              type="button"
              onClick={() => setCategory(c.value)}
              className={`rounded-full border px-3 py-1 text-sm font-medium transition-colors ${
                active
                  ? "border-giver-accent bg-giver-accent text-white"
                  : "border-slate-300 bg-white text-giver-slate hover:border-giver-accent hover:text-giver-accent"
              }`}
            >
              {c.label}
            </button>
          );
        })}
      </div>

      {error && <ErrorState message={error} />}
      {loading && <LoadingState title="Loading the feed…" subtitle="Fetching today's stories." />}

      {!loading && !error && items.length === 0 && (
        <p className="text-sm text-giver-slate">No stories found for this category right now.</p>
      )}

      {/* Card stack */}
      {!loading && !error && current && (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs text-giver-low">
            <span>
              Story {index + 1} of {items.length}
            </span>
            <span>{saved.length} saved</span>
          </div>

          <NewsFeedCard item={current} />

          <div className="flex items-center justify-center gap-3">
            <button
              type="button"
              onClick={advance}
              className="rounded-md border border-slate-300 bg-white px-5 py-2 text-sm font-medium text-giver-slate hover:border-giver-accent hover:text-giver-accent"
            >
              Skip
            </button>
            <button
              type="button"
              onClick={handleSave}
              className="rounded-md border border-emerald-300 bg-emerald-50 px-5 py-2 text-sm font-medium text-emerald-700 hover:bg-emerald-100"
            >
              {savedIds.has(current.id) ? "Saved ✓" : "Save"}
            </button>
            <Link
              href={current.detail_path}
              className="rounded-md bg-giver-accent px-5 py-2 text-sm font-semibold text-white hover:bg-blue-700"
            >
              Open
            </Link>
          </div>
        </div>
      )}

      {/* End of stack */}
      {atEnd && (
        <div className="rounded-xl border border-slate-200 bg-white p-6 text-center shadow-sm">
          <p className="text-sm font-semibold text-giver-ink">You&rsquo;re all caught up</p>
          <p className="mx-auto mt-1 max-w-md text-sm text-giver-slate">
            You went through every story in this category. Save list: {saved.length}.
          </p>
          <div className="mt-4 flex flex-wrap items-center justify-center gap-3">
            <button
              type="button"
              onClick={restart}
              className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-giver-slate hover:border-giver-accent hover:text-giver-accent"
            >
              Start over
            </button>
            <Link
              href="/dashboard"
              className="rounded-md bg-giver-accent px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
            >
              Open full dashboard
            </Link>
          </div>
        </div>
      )}

      {/* Saved list */}
      {saved.length > 0 && (
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-giver-low">
            Saved stories
          </p>
          <ul className="space-y-1">
            {saved.map((s) => (
              <li key={s.id} className="flex items-center justify-between gap-2 text-sm">
                <span className="truncate text-giver-slate">{s.headline}</span>
                <Link
                  href={s.detail_path}
                  className="shrink-0 text-xs font-medium text-giver-accent hover:underline"
                >
                  Open →
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Methodology */}
      {feed && (
        <details className="group rounded-lg border border-slate-200 bg-giver-mist">
          <summary className="flex cursor-pointer select-none items-center justify-between px-4 py-3 text-sm font-medium text-giver-ink">
            <span>How these signals work</span>
            <span className="text-giver-low transition-transform group-open:rotate-180">▾</span>
          </summary>
          <div className="space-y-3 border-t border-slate-200 px-4 py-3 text-xs text-giver-slate">
            <p>{feed.disclaimer}</p>
            <ul className="space-y-1.5">
              {feed.score_explanations.map((s) => (
                <li key={s.key}>
                  <span className="font-medium text-giver-ink">{s.label}</span>
                  {s.weighted ? (
                    <span className="ml-1 text-giver-accent">
                      ({Math.round(s.weight * 100)}% of ranking)
                    </span>
                  ) : (
                    <span className="ml-1 text-giver-low">(signal only)</span>
                  )}
                  <span className="block text-giver-slate">{s.description}</span>
                </li>
              ))}
            </ul>
            <p className="text-giver-low">
              Source mode: <span className="font-mono">{feed.provider_mode}</span>. Data falls back to
              fixtures if live providers are unavailable.
            </p>
          </div>
        </details>
      )}
    </div>
  );
}
