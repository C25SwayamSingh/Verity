"use client";

import { useRef, useState } from "react";
import { classifyLinkOnly } from "@/lib/ingest";

interface CheckerInputProps {
  onAnalyzeText: (text: string) => void;
  onAnalyzeMedia: (file: File) => void;
  loading?: boolean;
  initialText?: string;
}

const ACCEPT = ".mp4,.mov,.m4a,.mp3,.wav,audio/*,video/*";

export default function CheckerInput({
  onAnalyzeText,
  onAnalyzeMedia,
  loading,
  initialText = "",
}: CheckerInputProps) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [text, setText] = useState(initialText);
  const [file, setFile] = useState<File | null>(null);

  const hasFile = Boolean(file);
  const linkHint = classifyLinkOnly(text);
  const showLinkHint = !hasFile && linkHint.isLinkOnly;
  const canSubmit = (hasFile || text.trim().length >= 20) && !loading;

  function handleSubmit() {
    if (!canSubmit) return;
    if (file) {
      onAnalyzeMedia(file);
    } else {
      onAnalyzeText(text.trim());
    }
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <textarea
        rows={hasFile ? 4 : 9}
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste article text, a transcript, captions, or source notes — then press Analyze. (A bare video link can't be analyzed on its own.)"
        className="w-full resize-none rounded-xl border-0 px-2 py-2 text-base leading-relaxed text-giver-ink placeholder:text-giver-low focus:outline-none focus:ring-0"
        disabled={loading || hasFile}
      />

      {showLinkHint && (
        <div className="mb-2 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900">
          {linkHint.isSocialVideo
            ? "That looks like a video link only. The Giver can't watch or download it — attach a screen recording/audio, or paste the transcript, captions, or source notes."
            : "That looks like a link only. Paste the article text, a transcript, or source notes so The Giver has something to analyze."}
        </div>
      )}

      {hasFile && (
        <div className="mb-2 flex items-center justify-between rounded-xl bg-giver-mist px-3 py-2 text-sm">
          <span className="truncate text-giver-ink">
            <span className="font-medium">Attached:</span> {file?.name}
          </span>
          <button
            type="button"
            onClick={() => {
              setFile(null);
              if (fileRef.current) fileRef.current.value = "";
            }}
            className="ml-3 shrink-0 text-giver-low hover:text-giver-ink"
            disabled={loading}
            aria-label="Remove file"
          >
            Remove
          </button>
        </div>
      )}

      <div className="flex items-center justify-between gap-3 border-t border-slate-100 pt-3">
        <div>
          <input
            ref={fileRef}
            type="file"
            accept={ACCEPT}
            className="hidden"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            disabled={loading}
          />
          <button
            type="button"
            onClick={() => fileRef.current?.click()}
            disabled={loading}
            className="inline-flex items-center gap-1.5 rounded-lg px-2 py-1.5 text-sm text-giver-slate hover:bg-giver-mist disabled:opacity-50"
          >
            <span aria-hidden>＋</span> Attach audio / video
          </button>
        </div>

        <button
          type="button"
          onClick={handleSubmit}
          disabled={!canSubmit}
          className="rounded-xl bg-giver-accent px-6 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {loading ? "Analyzing…" : "Analyze"}
        </button>
      </div>
    </div>
  );
}
