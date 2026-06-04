import type { AnalyzeResponse } from "@/lib/types";
import ClaimCard from "./ClaimCard";
import FramingPanel from "./FramingPanel";
import NeutralRewrite from "./NeutralRewrite";

interface ResultsDashboardProps {
  data: AnalyzeResponse;
}

export default function ResultsDashboard({ data }: ResultsDashboardProps) {
  const eligible = data.eligibility.bias_framing_eligible;

  if (data.ingestion?.needs_more_input) {
    return <NeedsMoreInput data={data} />;
  }

  return (
    <div className="space-y-6">
      {data.ingestion?.transparency_note && (
        <section className="rounded-lg border border-sky-200 bg-sky-50 p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-sky-900">
            Source basis
          </p>
          <p className="mt-1 text-sm leading-relaxed text-sky-950">
            {data.ingestion.transparency_note}
          </p>
          {data.ingestion.source_links?.length > 0 && (
            <p className="mt-2 truncate text-xs text-sky-800">
              Link: {data.ingestion.source_links[0]}
            </p>
          )}
        </section>
      )}

      {data.media_source && (
        <section className="rounded-lg border border-amber-200 bg-amber-50 p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-amber-900">
            {data.media_source.input_basis_label}
          </p>
          <p className="mt-1 text-sm text-amber-950 leading-relaxed">
            {data.media_source.transparency_note}
          </p>
          <p className="mt-2 text-xs text-amber-800">
            File: {data.media_source.original_filename}
            {data.media_source.transcription_provider
              ? ` · Transcription: ${data.media_source.transcription_provider}`
              : ""}
          </p>
        </section>
      )}

      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-sm font-semibold text-giver-ink">Summary</h2>
        <p className="mt-2 text-sm leading-relaxed text-giver-slate">{data.summary}</p>
      </section>

      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-sm font-semibold text-giver-ink">Key takeaways</h2>
        <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-giver-slate">
          {data.key_takeaways.map((t, i) => (
            <li key={i}>{t}</li>
          ))}
        </ul>
      </section>

      <section
        className={`rounded-lg border p-5 ${
          eligible ? "border-emerald-200 bg-emerald-50" : "border-amber-200 bg-amber-50"
        }`}
      >
        <h2 className="text-sm font-semibold text-giver-ink">Content eligibility</h2>
        <p className="mt-1 text-xs text-giver-slate">
          Detected category: <strong>{data.eligibility.detected_category}</strong>
          {" · "}
          Framing &amp; alignment:{" "}
          <strong>{eligible ? "available" : "not available"}</strong>
        </p>
        <p className="mt-2 text-sm text-giver-slate">{data.eligibility.reason}</p>
      </section>

      {data.notes && data.notes.length > 0 && (
        <section className="rounded-lg border border-slate-200 bg-white p-5">
          <h2 className="text-sm font-semibold text-giver-ink">Notes</h2>
          <ul className="mt-2 list-disc pl-5 text-sm text-giver-slate">
            {data.notes.map((n, i) => (
              <li key={i}>{n}</li>
            ))}
          </ul>
        </section>
      )}

      <section>
        <h2 className="mb-3 text-sm font-semibold text-giver-ink">
          Extracted claims &amp; cross-source corroboration
        </h2>
        <div className="space-y-4">
          {data.claims.map((c) => (
            <ClaimCard key={c.claim_id} claim={c} showAlignment={eligible} />
          ))}
        </div>
      </section>

      <FramingPanel framing={data.framing} eligible={eligible} />
      <NeutralRewrite text={data.neutral_rewrite} eligible={eligible} />
    </div>
  );
}

function NeedsMoreInput({ data }: ResultsDashboardProps) {
  const ingestion = data.ingestion!;
  const isVideo = ingestion.ingestion_type === "social_video_url";

  return (
    <div className="space-y-5">
      <section className="rounded-lg border border-amber-200 bg-amber-50 p-5">
        <h2 className="text-sm font-semibold text-amber-900">
          {isVideo ? "Video link received — transcript or upload required" : "Link received — text required"}
        </h2>
        <p className="mt-2 text-sm leading-relaxed text-amber-950">
          {ingestion.guidance ??
            "We found a link, but no transcript or analyzable text was provided. Add a transcript, upload, or source notes so The Giver can analyze the content."}
        </p>
      </section>

      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-sm font-semibold text-giver-ink">What you can do next</h2>
        <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-giver-slate">
          <li>Upload a screen recording, video, or audio of the post.</li>
          <li>Paste the transcript or on-screen captions.</li>
          <li>Paste source notes or third-party key points.</li>
          <li>Paste the full article text (for written articles).</li>
        </ul>
        <p className="mt-3 text-xs text-giver-low">
          The Giver analyzes submitted or generated text. It does not download or scrape social videos.
        </p>
      </section>

      {ingestion.source_links?.length > 0 && (
        <section className="rounded-lg border border-slate-200 bg-white p-5">
          <h2 className="text-sm font-semibold text-giver-ink">Source link (metadata only)</h2>
          <ul className="mt-2 space-y-1 text-sm">
            {ingestion.source_links.map((link, i) => (
              <li key={i} className="truncate text-giver-slate">
                {link}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
