export type ContentType = "article" | "transcript" | "pasted_text";

export type UserCategory =
  | "breaking"
  | "domestic_us"
  | "foreign_world"
  | "markets_stocks"
  | "tech_ai"
  | "other";

export type ClaimType =
  | "factual_claim"
  | "opinion"
  | "advice"
  | "prediction"
  | "personal_experience"
  | "promotional_claim"
  | "unclear";

export type CorroborationStatus =
  | "high_corroboration"
  | "medium_corroboration"
  | "low_corroboration"
  | "contradicted"
  | "not_checkable";

export interface SourceRef {
  source_id: string;
  title: string;
  publisher: string;
  url: string;
  snippet: string;
  relevance_score: number;
}

export interface ClaimResult {
  claim_id: string;
  text: string;
  claim_type: ClaimType;
  corroboration_status: CorroborationStatus;
  supporting_sources: SourceRef[];
  contradicting_sources: SourceRef[];
  explanation: string;
}

export interface FramingIndicator {
  indicator_type: string;
  description: string;
  examples: string[];
}

export interface FramingResult {
  overall_label: string;
  indicators: FramingIndicator[];
}

export interface EligibilityResult {
  bias_framing_eligible: boolean;
  detected_category: string;
  reason: string;
}

export interface AnalyzeResponse {
  analysis_id: string;
  summary: string;
  key_takeaways: string[];
  claims: ClaimResult[];
  framing: FramingResult;
  neutral_rewrite: string;
  eligibility: EligibilityResult;
  notes?: string[];
}

export interface AnalyzeRequest {
  text: string;
  content_type: ContentType;
  user_selected_category: UserCategory;
}

export interface RateLimitError {
  error: string;
  message: string;
  retry_after_seconds: number;
}
