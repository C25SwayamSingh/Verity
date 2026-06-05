"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useCallback, useEffect, useState } from "react";
import CreatorDisclaimer from "@/components/CreatorDisclaimer";
import ErrorState from "@/components/ErrorState";
import LoadingState from "@/components/LoadingState";
import { ApiError, createDemoCreatorPost, getCreators } from "@/lib/api";
import {
  DEFAULT_INPUT_BASIS,
  INPUT_BASIS_OPTIONS,
  inputBasisFormHelp,
  type InputBasis,
} from "@/lib/inputBasis";
import type { CreatorListItem } from "@/lib/types";

const MIN_CONTENT_CHARS = 80;

const CREATOR_IDS = ["creator-001", "creator-002", "creator-003", "creator-004"];

const CONTENT_TYPES = [
  { value: "transcript", label: "Transcript" },
  { value: "article", label: "Article" },
  { value: "pasted_text", label: "Pasted text" },
] as const;

function DemoPostFormInner() {
  const searchParams = useSearchParams();
  const prefillCreator = searchParams.get("creator_id") ?? "";

  const [creators, setCreators] = useState<CreatorListItem[]>([]);
  const [creatorsLoading, setCreatorsLoading] = useState(true);

  const [creatorId, setCreatorId] = useState(prefillCreator);
  const [title, setTitle] = useState("");
  const [platform, setPlatform] = useState("Instagram");
  const [inputBasis, setInputBasis] = useState<InputBasis>(DEFAULT_INPUT_BASIS);
  const [sourceUrl, setSourceUrl] = useState("");
  const [topic, setTopic] = useState("");
  const [summary, setSummary] = useState("");
  const [content, setContent] = useState("");
  const [contentType, setContentType] =
    useState<(typeof CONTENT_TYPES)[number]["value"]>("pasted_text");
  const [postId, setPostId] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<{
    creatorId: string;
    postId: string;
    message: string;
  } | null>(null);

  useEffect(() => {
    if (prefillCreator) setCreatorId(prefillCreator);
  }, [prefillCreator]);

  useEffect(() => {
    let cancelled = false;
    getCreators()
      .then((res) => {
        if (!cancelled) setCreators(res.creators);
      })
      .catch(() => {
        if (!cancelled) setCreators([]);
      })
      .finally(() => {
        if (!cancelled) setCreatorsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const buildAnalyzableContent = useCallback(() => {
    const body = content.trim();
    const sum = summary.trim();
    if (sum) return `${sum}\n\n${body}`;
    return body;
  }, [content, summary]);

  const contentLength = buildAnalyzableContent().length;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    const cid = creatorId.trim();
    if (!cid) {
      setError("Select or enter a creator ID (e.g. creator-001).");
      return;
    }
    if (!title.trim()) {
      setError("Post title is required.");
      return;
    }
    if (!topic.trim()) {
      setError("Topic is required (e.g. monetary policy, AI regulation).");
      return;
    }
    const analyzable = buildAnalyzableContent();
    if (analyzable.length < MIN_CONTENT_CHARS) {
      setError(
        `Submitted text must be at least ${MIN_CONTENT_CHARS} characters after combining with optional summary (currently ${analyzable.length}).`,
      );
      return;
    }

    setSubmitting(true);
    try {
      const result = await createDemoCreatorPost(cid, {
        title: title.trim(),
        content: analyzable,
        topic: topic.trim(),
        platform: platform.trim() || "manual",
        source_url: sourceUrl.trim(),
        content_type: contentType,
        input_basis: inputBasis,
        ...(postId.trim() ? { post_id: postId.trim() } : {}),
      });
      setSuccess({
        creatorId: cid,
        postId: result.post.post_id,
        message: result.message,
      });
      setContent("");
      setSummary("");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError(err instanceof Error ? err.message : "Failed to submit demo post.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3">
        <p className="text-xs font-semibold uppercase tracking-wide text-amber-900">
          Internal demo tool only
        </p>
        <p className="mt-1 text-sm text-amber-950 leading-relaxed">
          Add <strong>provided source notes</strong>, rough transcripts, captions, or third-party
          key points (e.g. Fofo-style extracts) to a fixture creator&apos;s{" "}
          <strong>sample integrity profile</strong>. Verity analyzes{" "}
          <strong>submitted text only</strong> — it does not watch, download, or transcribe
          Instagram/TikTok videos unless you supply a full transcript. Not creator onboarding.
        </p>
      </div>

      <div>
        <h2 className="text-lg font-semibold text-giver-ink">Add demo creator post</h2>
        <p className="mt-1 text-sm text-giver-slate">
          Builds <strong>claim support</strong>, <strong>source alignment</strong>,{" "}
          <strong>cross-source corroboration</strong>, and <strong>framing indicators</strong> for
          the selected profile. Choose an accurate <strong>input basis</strong> so the dashboard
          does not imply a verbatim transcript when you only have key points.
        </p>
      </div>

      <CreatorDisclaimer compact />

      {success && (
        <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-5 space-y-3">
          <p className="font-medium text-emerald-900">Demo post saved and analyzed</p>
          <p className="text-sm text-emerald-800">{success.message}</p>
          <p className="text-xs text-emerald-800">
            Post ID: <code className="rounded bg-white/80 px-1">{success.postId}</code>
          </p>
          <div className="flex flex-wrap gap-3 pt-1">
            <Link
              href={`/creators/${success.creatorId}`}
              className="inline-flex items-center rounded-md bg-emerald-800 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-900"
            >
              View sample integrity profile →
            </Link>
            <button
              type="button"
              onClick={() => setSuccess(null)}
              className="text-sm text-emerald-800 hover:underline"
            >
              Add another post
            </button>
          </div>
        </div>
      )}

      {error && (
        <ErrorState
          message={error}
          onRetry={() => setError(null)}
        />
      )}

      {submitting ? (
        <LoadingState
          title="Analyzing demo post…"
          subtitle="Running claim extraction, cross-source corroboration, and framing indicators. This may take a few seconds."
        />
      ) : (
        !success && (
          <form onSubmit={handleSubmit} className="space-y-5 rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <div className="space-y-1.5">
              <label htmlFor="creator_id" className="block text-sm font-medium text-giver-ink">
                Creator ID
              </label>
              <select
                id="creator_id"
                value={creatorId}
                onChange={(e) => setCreatorId(e.target.value)}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-giver-ink focus:border-giver-accent focus:outline-none focus:ring-1 focus:ring-giver-accent"
                disabled={creatorsLoading && creators.length === 0}
              >
                <option value="">Select a fixture creator…</option>
                {(creators.length > 0 ? creators : CREATOR_IDS.map((id) => ({ creator_id: id, name: id }))).map(
                  (c) => (
                    <option key={c.creator_id} value={c.creator_id}>
                      {c.creator_id}
                      {"name" in c && c.name !== c.creator_id ? ` — ${c.name}` : ""}
                    </option>
                  ),
                )}
              </select>
              <p className="text-xs text-giver-low">
                Fixture IDs: creator-001 … creator-004. Or type a custom ID below if the list fails to load.
              </p>
              <input
                type="text"
                value={creatorId}
                onChange={(e) => setCreatorId(e.target.value)}
                placeholder="creator-001"
                className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm text-giver-ink"
                aria-label="Creator ID override"
              />
            </div>

            <div className="space-y-1.5">
              <label htmlFor="title" className="block text-sm font-medium text-giver-ink">
                Post title
              </label>
              <input
                id="title"
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Fed holds rates steady — transcript excerpt"
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              />
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-1.5">
                <label htmlFor="platform" className="block text-sm font-medium text-giver-ink">
                  Source / platform
                </label>
                <input
                  id="platform"
                  type="text"
                  value={platform}
                  onChange={(e) => setPlatform(e.target.value)}
                  placeholder="Instagram, YouTube, Substack…"
                  className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                />
              </div>
              <div className="space-y-1.5">
                <label htmlFor="topic" className="block text-sm font-medium text-giver-ink">
                  Topic
                </label>
                <input
                  id="topic"
                  type="text"
                  required
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="monetary policy"
                  className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label htmlFor="source_url" className="block text-sm font-medium text-giver-ink">
                Original link (optional)
              </label>
              <input
                id="source_url"
                type="url"
                value={sourceUrl}
                onChange={(e) => setSourceUrl(e.target.value)}
                placeholder="https://…"
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              />
            </div>

            <div className="space-y-1.5">
              <label htmlFor="input_basis" className="block text-sm font-medium text-giver-ink">
                Input basis
              </label>
              <select
                id="input_basis"
                value={inputBasis}
                onChange={(e) => setInputBasis(e.target.value as InputBasis)}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              >
                {INPUT_BASIS_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
              <p className="text-xs text-giver-low leading-relaxed">
                {inputBasisFormHelp(inputBasis)}
              </p>
            </div>

            <div className="space-y-1.5">
              <label htmlFor="content_type" className="block text-sm font-medium text-giver-ink">
                Checker content type
              </label>
              <select
                id="content_type"
                value={contentType}
                onChange={(e) =>
                  setContentType(e.target.value as (typeof CONTENT_TYPES)[number]["value"])
                }
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              >
                {CONTENT_TYPES.map((ct) => (
                  <option key={ct.value} value={ct.value}>
                    {ct.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-1.5">
              <label htmlFor="summary" className="block text-sm font-medium text-giver-ink">
                Optional summary
              </label>
              <textarea
                id="summary"
                rows={2}
                value={summary}
                onChange={(e) => setSummary(e.target.value)}
                placeholder="Short context prepended to the analyzable text (optional)."
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              />
            </div>

            <div className="space-y-1.5">
              <label htmlFor="content" className="block text-sm font-medium text-giver-ink">
                Provided source notes / text
              </label>
              <textarea
                id="content"
                required
                rows={8}
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Paste Fofo-style key points, caption text, rough transcript, or full transcript (minimum 80 characters)…"
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm font-mono leading-relaxed"
              />
              <p
                className={`text-xs ${contentLength >= MIN_CONTENT_CHARS ? "text-giver-low" : "text-amber-700"}`}
              >
                {contentLength} / {MIN_CONTENT_CHARS} characters
                {summary.trim() ? " (includes optional summary)" : ""}
              </p>
            </div>

            <div className="space-y-1.5">
              <label htmlFor="post_id" className="block text-sm font-medium text-giver-ink">
                Post ID (optional — reuse to update existing demo post)
              </label>
              <input
                id="post_id"
                type="text"
                value={postId}
                onChange={(e) => setPostId(e.target.value)}
                placeholder="demo-abc123…"
                className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
              />
            </div>

            <div className="flex flex-wrap items-center gap-3 pt-2">
              <button
                type="submit"
                disabled={submitting}
                className="rounded-md bg-giver-accent px-5 py-2.5 text-sm font-medium text-white hover:opacity-90 disabled:opacity-50"
              >
                Save &amp; analyze demo post
              </button>
              <Link href="/creators" className="text-sm text-giver-accent hover:underline">
                ← Creator profiles
              </Link>
            </div>
          </form>
        )
      )}

      <footer className="pt-2 border-t border-slate-200 text-sm text-giver-low">
        <p>
          API: <code className="rounded bg-giver-mist px-1">POST /v1/creators/&#123;id&#125;/posts/demo</code>
          . See <code className="rounded bg-giver-mist px-1">docs/CREATOR_DEMO_WORKFLOW.md</code>.
        </p>
      </footer>
    </div>
  );
}

export default function CreatorDemoPostPage() {
  return (
    <Suspense
      fallback={
        <LoadingState
          title="Loading demo form…"
          subtitle="Internal tool for sample integrity profiles."
        />
      }
    >
      <DemoPostFormInner />
    </Suspense>
  );
}
