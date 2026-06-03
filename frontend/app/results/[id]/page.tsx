"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import ErrorState from "@/components/ErrorState";
import LoadingState from "@/components/LoadingState";
import ResultsDashboard from "@/components/ResultsDashboard";
import { getAnalysis } from "@/lib/api";
import type { AnalyzeResponse } from "@/lib/types";

export default function ResultsPage() {
  const params = useParams();
  const id = typeof params.id === "string" ? params.id : "";
  const [data, setData] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    getAnalysis(id)
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, [id]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-giver-ink">Analysis results</h2>
        <Link href="/" className="text-sm text-giver-accent hover:underline">
          ← New analysis
        </Link>
      </div>

      {loading && <LoadingState />}
      {error && <ErrorState message={error} />}
      {data && <ResultsDashboard data={data} />}
    </div>
  );
}
