import type {
  AnalyzeRequest,
  AnalyzeResponse,
  CreatorListResponse,
  CreatorOverview,
  CreatorPostsResponse,
  DashboardArticle,
  DashboardCategory,
  DashboardResponse,
  RateLimitError,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  body?: unknown;

  constructor(message: string, status: number, body?: unknown) {
    super(message);
    this.status = status;
    this.body = body;
  }
}

export async function analyzeContent(payload: AnalyzeRequest): Promise<AnalyzeResponse> {
  const res = await fetch(`${API_URL}/v1/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    if (res.status === 429) {
      const err = body as RateLimitError;
      throw new ApiError(
        err.message ?? "Too many requests",
        429,
        body,
      );
    }
    throw new ApiError(
      (body as { detail?: string }).detail ?? "Analysis failed",
      res.status,
      body,
    );
  }

  return res.json();
}

export async function getAnalysis(analysisId: string): Promise<AnalyzeResponse> {
  const res = await fetch(`${API_URL}/v1/analysis/${analysisId}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new ApiError("Analysis not found", res.status);
  }
  return res.json();
}

export async function getDashboardArticle(articleId: string): Promise<DashboardArticle> {
  const res = await fetch(
    `${API_URL}/v1/dashboard/articles/${encodeURIComponent(articleId)}`,
    { cache: "no-store" },
  );
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(
      (body as { detail?: string }).detail ?? "Article not found",
      res.status,
      body,
    );
  }
  return res.json();
}

export async function getDashboardArticles(
  category: DashboardCategory,
): Promise<DashboardResponse> {
  const res = await fetch(
    `${API_URL}/v1/dashboard/articles?category=${encodeURIComponent(category)}`,
    { cache: "no-store" },
  );
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(
      (body as { detail?: string }).detail ?? "Failed to load dashboard",
      res.status,
      body,
    );
  }
  return res.json();
}

export async function getCreators(): Promise<CreatorListResponse> {
  const res = await fetch(`${API_URL}/v1/creators`, { cache: "no-store" });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(
      (body as { detail?: string }).detail ?? "Failed to load creators",
      res.status,
      body,
    );
  }
  return res.json();
}

export async function getCreator(creatorId: string): Promise<CreatorOverview> {
  const res = await fetch(
    `${API_URL}/v1/creators/${encodeURIComponent(creatorId)}`,
    { cache: "no-store" },
  );
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(
      (body as { detail?: string }).detail ?? "Creator not found",
      res.status,
      body,
    );
  }
  return res.json();
}

export async function getCreatorPosts(creatorId: string): Promise<CreatorPostsResponse> {
  const res = await fetch(
    `${API_URL}/v1/creators/${encodeURIComponent(creatorId)}/posts`,
    { cache: "no-store" },
  );
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(
      (body as { detail?: string }).detail ?? "Creator posts not found",
      res.status,
      body,
    );
  }
  return res.json();
}
