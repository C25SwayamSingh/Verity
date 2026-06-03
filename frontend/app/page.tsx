"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import ArticleInput from "@/components/ArticleInput";
import ErrorState from "@/components/ErrorState";
import LoadingState from "@/components/LoadingState";
import { analyzeContent, ApiError } from "@/lib/api";
import type { UserCategory } from "@/lib/types";

export default function HomePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retryAfter, setRetryAfter] = useState<number | undefined>();

  async function handleAnalyze(text: string, category: UserCategory) {
    setLoading(true);
    setError(null);
    setRetryAfter(undefined);
    try {
      const result = await analyzeContent({
        text,
        content_type: "article",
        user_selected_category: category,
      });
      router.push(`/results/${result.analysis_id}`);
    } catch (e) {
      if (e instanceof ApiError && e.status === 429) {
        const body = e.body as { retry_after_seconds?: number; message?: string };
        setRetryAfter(body?.retry_after_seconds);
        setError(body?.message ?? "Too many requests.");
      } else {
        setError(e instanceof Error ? e.message : "Analysis failed.");
      }
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-giver-ink">Core Checker</h2>
        <p className="mt-1 text-sm text-giver-slate">
          Paste news or article text for summary, claim extraction, fixture-based cross-source
          corroboration, framing indicators, and a neutral rewrite.
        </p>
      </div>

      {error && (
        <ErrorState
          message={error}
          retryAfterSeconds={retryAfter}
          onRetry={() => {
            setError(null);
            setRetryAfter(undefined);
          }}
        />
      )}

      {loading ? <LoadingState /> : <ArticleInput onAnalyze={handleAnalyze} loading={loading} />}
    </div>
  );
}
