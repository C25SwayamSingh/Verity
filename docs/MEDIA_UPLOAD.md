# Media Upload — Phase 4A

User-provided **uploaded media** only. No Instagram/TikTok download, scraping, or link-based ingestion.

> **Core ingestion rule (Phase 4C):** Verity analyzes *analyzable text* — pasted text, article text, a transcript, captions, or source notes — or a transcript generated from uploaded media. It **never** treats a raw social/video URL as content. If you paste only an Instagram/TikTok/YouTube link with no text, the checker returns a clear "transcript or upload required" state and keeps the link as source metadata only. Full news bias/framing analysis runs only for supported news/current-information categories; a neutral/clearer rewrite is still available for other content when there is enough analyzable text.
>
> **Article-URL extraction (Phase 4D):** when you share a normal **article** link (a news site or blog), Verity fetches that page and extracts the main article text, then analyzes the real content (results show a "Source basis" note). This applies to article pages only — **social/video links (Instagram/TikTok/YouTube) are never fetched or downloaded** and still require an uploaded recording or a pasted transcript. Extraction can be tuned/disabled via `ARTICLE_EXTRACTION_*` settings; paywalled or JS-only pages may yield little text and fall back to the "paste text" state.

---

## What it does

1. User uploads **mp4**, **mov**, **m4a**, **mp3**, or **wav** on the Core Checker (`/`).
2. Backend extracts audio from video (requires **ffmpeg** when `TRANSCRIPTION_PROVIDER` is not `mock`).
3. A **transcription provider** converts audio to text (mock by default; OpenAI Whisper when configured).
4. Transcript runs through the existing **`IngestService.analyze()`** pipeline (claims, corroboration, framing, neutral rewrite).
5. Results appear on **`/results/{analysis_id}`** with a transparency banner.

---

## Supported formats

| Type | Extensions | Input basis stored |
|------|------------|-------------------|
| Video | `.mp4`, `.mov` | `uploaded_video_transcript` |
| Audio | `.mp3`, `.m4a`, `.wav` | `uploaded_audio_transcript` |
| Screen recording | `.mp4`, `.mov` (select “Screen recording”) | `uploaded_screen_recording_transcript` |

**Max size:** 50 MB default (`MEDIA_MAX_UPLOAD_BYTES`).

---

## Transcription providers

| `TRANSCRIPTION_PROVIDER` | Behavior |
|--------------------------|----------|
| `mock` (default) | Deterministic sample transcript; no network; no ffmpeg for video in dev |
| `openai` | Uses OpenAI Whisper when `OPENAI_API_KEY` is set; falls back to mock if key missing |

Swap providers via `app/services/transcription/` adapter pattern.

---

## Social video workflow (Instagram Reels, etc.)

Verity **does not**:

- Download Reels from a pasted link
- Transcribe TikTok/Instagram by URL
- Verify the full original video

**Supported approaches:**

1. **Upload a screen recording** of the Reel (mp4/mov) → generated transcript → analysis.
2. **Paste source notes** or Fofo-style key points via `/creators/demo` with correct **input basis**.
3. **Paste a full transcript** on `/` if you have one.

Optional **original link** on upload is stored as **metadata only**.

---

## API

`POST /v1/analyze/media` — `multipart/form-data`

| Field | Required | Notes |
|-------|----------|-------|
| `file` | yes | Media file |
| `user_selected_category` | no | default `domestic_us` |
| `media_kind` | no | `video`, `audio`, `screen_recording` |
| `title` | no | Shown in transcript preamble |
| `source_url` | no | Metadata only |

Rate-limited with `POST /v1/analyze`.

---

## Trust language

- “Analysis based on transcript generated from uploaded media.”
- Not: downloaded from Instagram, official platform transcript, full video verified.

---

## Limitations

- Single-file upload only (no batch)
- No media library or study mode
- Video processing needs ffmpeg (except mock dev mode)
- Transcript quality depends on audio clarity and provider
- Uploaded video files are not stored long-term — transcript + analysis JSON in SQLite
