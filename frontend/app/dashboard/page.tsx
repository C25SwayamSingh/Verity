"use client";

import { useEffect, useState } from "react";
import DashboardArticleCard from "@/components/DashboardArticleCard";
import ErrorState from "@/components/ErrorState";
import LoadingState from "@/components/LoadingState";
import { getDashboardArticles } from "@/lib/api";
import type { DashboardArticle, DashboardCategory } from "@/lib/types";

const CATEGORIES: { value: DashboardCategory; label: string }[] = [
  { value: "breaking", label: "Breaking" },
  { value: "domestic_us", label: "Domestic / U.S." },
  { value: "foreign_world", label: "Foreign / World" },
  { value: "markets_stocks", label: "Markets / Stocks" },
  { value: "tech_ai", label: "Tech & AI" },
];

const CATEGORY_LABEL: Record<DashboardCategory, string> = Object.fromEntries(
  CATEGORIES.map((c) => [c.value, c.label]),
) as Record<DashboardCategory, string>;

export default function DashboardPage() {
  const [category, setCategory] = useState<DashboardCategory>("breaking");
  const [articles, setArticles] = useState<DashboardArticle[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    setArticles([]);

    getDashboardArticles(category)
      .then((res) => {
        if (!cancelled) setArticles(res.articles);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load dashboard.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [category]);

  return (
    <div className="space-y-6">

      {/* Page header */}
      <div>
        <h2 className="text-lg font-semibold text-giver-ink">Reliable News Dashboard</h2>
        <p className="mt-1 text-sm text-giver-slate">
          Top 5 articles per category, ranked by a composite integrity score using
          importance, credibility, relevance, freshness, and source diversity.
          All data is fixture-based — no live news sources are connected yet.
        </p>
      </div>

      {/* Methodology disclosure */}
      <details className="group rounded-lg border border-slate-200 bg-giver-mist">
        <summary className="flex cursor-pointer select-none items-center justify-between px-4 py-3 text-sm font-medium text-giver-ink">
          <span>Methodology — how articles are scored</span>
          <span className="text-giver-low transition-transform group-open:rotate-180">▾</span>
        </summary>
        <div className="border-t border-slate-200 px-4 py-3 text-xs text-giver-slate space-y-2">
          <p>
            Each article receives a <strong className="text-giver-ink">final score</strong> (0–100)
            computed from five component signals:
          </p>
          <table className="w-full text-xs">
            <thead>
              <tr className="text-left text-giver-low">
                <th className="pb-1 font-medium">Signal</th>
                <th className="pb-1 font-medium text-right">Weight</th>
                <th className="pb-1 pl-4 font-medium">What it measures</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {[
                ["Importance", "35%", "Significance of the story to the broader public"],
                ["Credibility", "30%", "Reliability of the source and corroboration quality"],
                ["Relevance", "20%", "How closely the article matches the selected category"],
                ["Freshness", "10%", "Recency relative to publication time"],
                ["Source Diversity", "5%", "Number of independent outlets covering the same story"],
              ].map(([signal, weight, desc]) => (
                <tr key={signal} className="align-top">
                  <td className="py-1 font-medium text-giver-ink whitespace-nowrap">{signal}</td>
                  <td className="py-1 text-right font-semibold text-giver-accent whitespace-nowrap">{weight}</td>
                  <td className="py-1 pl-4 text-giver-slate">{desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="font-mono text-[11px] text-giver-low bg-white rounded border border-slate-200 px-3 py-2 mt-1 leading-relaxed">
            final_score = 0.35 × importance + 0.30 × credibility + 0.20 × relevance
            <br />
            {"                  "}+ 0.10 × freshness + 0.05 × source_diversity
          </p>
          <p className="text-giver-low">
            Scores are fixture/mock values for the Phase 2 scaffold. Live scoring will use real
            source data.
          </p>
        </div>
      </details>

      {/* Category selector */}
      <div className="flex items-center gap-3">
        <label htmlFor="category-select" className="text-sm font-medium text-giver-ink shrink-0">
          Category
        </label>
        <select
          id="category-select"
          value={category}
          onChange={(e) => setCategory(e.target.value as DashboardCategory)}
          className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm text-giver-ink shadow-sm focus:border-giver-accent focus:outline-none focus:ring-1 focus:ring-giver-accent"
        >
          {CATEGORIES.map((c) => (
            <option key={c.value} value={c.value}>
              {c.label}
            </option>
          ))}
        </select>
      </div>

      {error && <ErrorState message={error} />}
      {loading && <LoadingState />}

      {!loading && !error && articles.length === 0 && (
        <p className="text-sm text-giver-slate">No articles found for this category.</p>
      )}

      {!loading && !error && articles.length > 0 && (
        <>
          <p className="text-xs font-medium text-giver-low uppercase tracking-wide">
            Top {articles.length} · {CATEGORY_LABEL[category]}
          </p>
          <div className="space-y-4">
            {articles.map((article, i) => (
              <DashboardArticleCard key={article.id} article={article} rank={i + 1} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
