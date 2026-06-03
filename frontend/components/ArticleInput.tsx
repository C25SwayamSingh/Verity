"use client";

import { useState } from "react";
import type { UserCategory } from "@/lib/types";

const CATEGORIES: { value: UserCategory; label: string }[] = [
  { value: "breaking", label: "Breaking news" },
  { value: "domestic_us", label: "Domestic (U.S.)" },
  { value: "foreign_world", label: "Foreign / world" },
  { value: "markets_stocks", label: "Markets & stocks" },
  { value: "tech_ai", label: "Tech & AI" },
  { value: "other", label: "Other" },
];

interface ArticleInputProps {
  onAnalyze: (text: string, category: UserCategory) => void;
  loading?: boolean;
}

export default function ArticleInput({ onAnalyze, loading }: ArticleInputProps) {
  const [text, setText] = useState("");
  const [category, setCategory] = useState<UserCategory>("domestic_us");

  const canSubmit = text.trim().length >= 20 && !loading;

  return (
    <div className="space-y-4 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <div>
        <label htmlFor="category" className="mb-1 block text-sm font-medium text-giver-slate">
          Content category
        </label>
        <select
          id="category"
          value={category}
          onChange={(e) => setCategory(e.target.value as UserCategory)}
          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          disabled={loading}
        >
          {CATEGORIES.map((c) => (
            <option key={c.value} value={c.value}>
              {c.label}
            </option>
          ))}
        </select>
        <p className="mt-1 text-xs text-giver-slate">
          The engine also classifies from your text; non-news content may limit framing analysis.
        </p>
      </div>

      <div>
        <label htmlFor="article-text" className="mb-1 block text-sm font-medium text-giver-slate">
          Article or news text
        </label>
        <textarea
          id="article-text"
          rows={12}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste article or transcript text here…"
          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm leading-relaxed"
          disabled={loading}
        />
      </div>

      <button
        type="button"
        disabled={!canSubmit}
        onClick={() => onAnalyze(text.trim(), category)}
        className="w-full rounded-md bg-giver-accent px-4 py-3 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50 hover:bg-blue-700"
      >
        {loading ? "Analyzing…" : "Analyze"}
      </button>
    </div>
  );
}
