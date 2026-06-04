# Social Video Limitations — The Giver

The Giver **does not download, scrape, or auto-transcribe social videos** from a
pasted link. This is a deliberate product and legal/platform-risk decision, not a
missing feature.

## What we do NOT do

- ❌ No Instagram / TikTok / YouTube / X / Facebook downloading.
- ❌ No scraping of social or article pages from a bare link.
- ❌ No automatic transcription of a video just because its URL was pasted.
- ❌ No generating a summary, key takeaways, extracted claims, or neutral rewrite
  from a **URL string**.

## What happens when only a social/video link is submitted

The checker classifies the input (`backend/app/core/ingestion.py`). A link-only
social/video submission returns a clear "needs more input" state instead of
fabricating analysis:

> "We found a video link, but no transcript or analyzable text was provided.
> Upload the video, screen recording, or audio, paste a transcript or captions,
> or add source notes so The Giver can analyze the actual content. The Giver does
> not download or scrape social videos."

In that state:

- `ingestion.needs_more_input = true`, `ingestion.ingestion_type = "social_video_url"`
- `summary` is the guidance message; `key_takeaways = []`, `claims = []`,
  `neutral_rewrite = ""`
- The URL is retained in `ingestion.source_links` as **metadata only**.

This is enforced by tests in `backend/tests/test_ingestion.py` (e.g.
`test_url_only_instagram_does_not_fabricate_content`).

## How to actually analyze social video content

Provide real analyzable text or media — then the normal pipeline runs:

1. **Upload** the video / screen recording / audio (`POST /v1/analyze/media`) —
   it is transcribed locally (mock provider by default; Whisper if configured).
2. **Paste a transcript or captions** into the checker.
3. **Paste source notes / third-party key points** describing the content.

Pasted **article** links (non-social) may be fetched and parsed for their body
text when `ARTICLE_EXTRACTION_ENABLED=true` (Phase 4D) — social/video URLs are
always skipped.

## News Integrity Feed

The home feed shows **news articles** from news providers (fixtures / RSS /
GDELT). It never embeds, downloads, or transcribes social videos. Social links
remain metadata throughout the product.
