// Lightweight, client-side mirror of the backend ingestion classifier.
// Used only to show an inline hint before submitting — the backend is the
// source of truth. Verity never downloads or scrapes linked content.

const URL_RE = /https?:\/\/[^\s<>"')]+/gi;
const BARE_DOMAIN_RE =
  /\b(?:www\.)?[a-z0-9-]+\.(?:com|org|net|io|gov|co|tv|watch|be)\b[^\s]*/gi;

const SOCIAL_VIDEO_DOMAINS = [
  "instagram.com",
  "tiktok.com",
  "youtube.com",
  "youtu.be",
  "facebook.com",
  "fb.watch",
  "twitter.com",
  "x.com",
  "reddit.com",
  "snapchat.com",
  "twitch.tv",
  "vimeo.com",
  "threads.net",
];

const MIN_CHARS = 25;
const MIN_WORDS = 5;

export function extractUrls(text: string): string[] {
  const matched = text.match(URL_RE);
  if (matched && matched.length) return matched;
  const bare = text.match(BARE_DOMAIN_RE);
  return bare ?? [];
}

export function isSocialVideoUrl(url: string): boolean {
  const host = url
    .replace(/^https?:\/\//i, "")
    .split("/")[0]
    .toLowerCase()
    .replace(/^www\./, "");
  return SOCIAL_VIDEO_DOMAINS.some((d) => host === d || host.endsWith("." + d));
}

function residual(text: string): string {
  return text.replace(URL_RE, " ").replace(BARE_DOMAIN_RE, " ").replace(/\s+/g, " ").trim();
}

export interface LinkOnlyHint {
  isLinkOnly: boolean;
  isSocialVideo: boolean;
}

export function classifyLinkOnly(text: string): LinkOnlyHint {
  const trimmed = text.trim();
  const urls = extractUrls(trimmed);
  if (!urls.length) return { isLinkOnly: false, isSocialVideo: false };

  const res = residual(trimmed);
  const words = res.split(/\s+/).filter((w) => /[a-z]/i.test(w));
  const analyzable = res.length >= MIN_CHARS && words.length >= MIN_WORDS;
  if (analyzable) return { isLinkOnly: false, isSocialVideo: false };

  return { isLinkOnly: true, isSocialVideo: urls.some(isSocialVideoUrl) };
}
