"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useRef, useState } from "react";
import CheckerInput from "@/components/CheckerInput";
import ErrorState from "@/components/ErrorState";
import LoadingState from "@/components/LoadingState";
import { analyzeContent, analyzeMediaUpload, ApiError } from "@/lib/api";

function buildSharedText(params: URLSearchParams): { text: string; autoRun: boolean } {
  const title = params.get("title")?.trim() ?? "";
  const text = params.get("text")?.trim() ?? "";
  const url = params.get("url")?.trim() ?? "";

  const pieces = [title, text, url].filter(Boolean);
  const combined = pieces.join("\n");

  // Auto-run only when there is real shared text/caption (not just a bare link).
  const autoRun = text.length >= 40;
  return { text: combined, autoRun };
}

function HomeInner() {
  const router = useRouter();
  const params = useSearchParams();
  const { text: sharedText, autoRun } = buildSharedText(
    new URLSearchParams(params.toString()),
  );

  const [loading, setLoading] = useState(false);
  const [mediaLoading, setMediaLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retryAfter, setRetryAfter] = useState<number | undefined>();
  const autoRan = useRef(false);

  const busy = loading || mediaLoading;

  function handleError(e: unknown, fallback: string) {
    if (e instanceof ApiError && e.status === 429) {
      const body = e.body as { retry_after_seconds?: number; message?: string };
      setRetryAfter(body?.retry_after_seconds);
      setError(body?.message ?? "Too many requests.");
    } else {
      setError(e instanceof Error ? e.message : fallback);
    }
  }

  async function handleAnalyzeText(text: string) {
    setLoading(true);
    setError(null);
    setRetryAfter(undefined);
    try {
      const result = await analyzeContent({
        text,
        content_type: "article",
        user_selected_category: "domestic_us",
      });
      router.push(`/results/${result.analysis_id}`);
    } catch (e) {
      handleError(e, "Analysis failed.");
      setLoading(false);
    }
  }

  async function handleAnalyzeMedia(file: File) {
    setMediaLoading(true);
    setError(null);
    setRetryAfter(undefined);
    try {
      const fd = new FormData();
      fd.append("file", file);
      fd.append("media_kind", "auto");
      fd.append("user_selected_category", "domestic_us");
      const result = await analyzeMediaUpload(fd);
      router.push(`/results/${result.analysis_id}`);
    } catch (e) {
      handleError(e, "Media analysis failed.");
      setMediaLoading(false);
    }
  }

  useEffect(() => {
    if (autoRan.current) return;
    if (autoRun && sharedText.trim().length >= 20) {
      autoRan.current = true;
      handleAnalyzeText(sharedText.trim());
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoRun, sharedText]);

  return (
    <div className="mx-auto max-w-2xl space-y-5">
      <div className="text-center">
        <h2 className="text-2xl font-semibold text-giver-ink">Check any post</h2>
        <p className="mx-auto mt-2 max-w-lg text-sm text-giver-slate">
          Paste article text, a transcript, captions, or source notes — or attach an audio/video
          clip or screen recording. The Giver returns claim support, cross-source corroboration,
          framing indicators, and a neutral rewrite.
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

      {busy ? (
        <LoadingState
          title={mediaLoading ? "Transcribing and analyzing…" : "Analyzing…"}
          subtitle={
            mediaLoading
              ? "Generating a transcript from your media, then running the information-integrity engine."
              : "Extracting claims, checking source alignment, and reviewing framing."
          }
        />
      ) : (
        <>
          <CheckerInput
            onAnalyzeText={handleAnalyzeText}
            onAnalyzeMedia={handleAnalyzeMedia}
            loading={busy}
            initialText={sharedText}
          />
          <p className="text-center text-xs text-giver-low">
            Category is detected automatically. A pasted Instagram/TikTok/YouTube link is kept as
            source metadata only — The Giver does not download or scrape videos. For a Reel, attach a
            screen recording or its audio, or paste the transcript/source notes.
          </p>
        </>
      )}
    </div>
  );
}

export default function HomePage() {
  return (
    <Suspense fallback={<LoadingState title="Loading…" subtitle="Preparing the checker." />}>
      <HomeInner />
    </Suspense>
  );
}
