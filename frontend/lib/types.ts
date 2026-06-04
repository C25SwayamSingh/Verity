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

export interface IngestionInfo {
  ingestion_type: string;
  analyzable: boolean;
  needs_more_input: boolean;
  source_links: string[];
  guidance?: string | null;
  transparency_note?: string | null;
}

export interface MediaSourceMetadata {
  input_basis: string;
  input_basis_label: string;
  transparency_note: string;
  original_filename: string;
  source_url?: string;
  title?: string;
  transcript_char_count: number;
  transcription_provider: string;
  media_kind: string;
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
  ingestion?: IngestionInfo | null;
  media_source?: MediaSourceMetadata | null;
  generated_transcript?: string | null;
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

export type DashboardCategory =
  | "breaking"
  | "domestic_us"
  | "foreign_world"
  | "markets_stocks"
  | "tech_ai";

export interface DashboardArticle {
  id: string;
  headline: string;
  source: string;
  category: string;
  published_at: string;
  neutral_summary: string;
  importance_score: number;
  credibility_score: number;
  relevance_score: number;
  freshness_score: number;
  source_diversity_score: number;
  final_score: number;
  framing_label: string;
  key_claims: string[];
  support_summary: string;
  contradiction_warnings: string[];
  why_selected: string;
}

export interface DashboardResponse {
  category: string;
  articles: DashboardArticle[];
}

// ---------------------------------------------------------------------------
// Creator / Influencer Integrity Dashboard — Phase 3
// ---------------------------------------------------------------------------

export interface WeakClaim {
  claim_id: string;
  post_id: string;
  text: string;
  corroboration_status: string;
  note: string;
}

export interface CreatorListItem {
  creator_id: string;
  name: string;
  platform: string;
  handle: string;
  category: string;
  bio: string;
  metrics_source?: string;
  total_analyzed_posts: number;
  source_alignment_score: number;
  claim_support_rate: number;
  contradiction_rate: number;
  top_topics: string[];
}

export interface CreatorListResponse {
  creators: CreatorListItem[];
}

export interface CreatorOverview {
  creator_id: string;
  name: string;
  platform: string;
  handle: string;
  category: string;
  bio: string;
  metrics_source?: string;
  total_analyzed_posts: number;
  source_alignment_score: number;
  claim_support_rate: number;
  contradiction_rate: number;
  low_corroboration_rate: number;
  source_diversity_score: number;
  average_framing_score: number;
  top_topics: string[];
  most_used_sources: string[];
  most_reliable_posts: string[];
  weakest_claims: WeakClaim[];
  transparency_summary: string;
}

export interface PostClaim {
  claim_id: string;
  text: string;
  claim_type: string;
  corroboration_status: string;
}

export interface CreatorPost {
  post_id: string;
  creator_id: string;
  title: string;
  platform: string;
  published_at: string;
  source_url: string;
  topic: string;
  summary: string;
  metrics_source?: string;
  claims: PostClaim[];
  supported_claims_count: number;
  contradicted_claims_count: number;
  low_corroboration_claims_count: number;
  source_alignment_score: number;
  framing_label: string;
  sources_used: string[];
  audience_signal_placeholder: string;
  input_basis?: string | null;
  input_basis_label?: string | null;
  input_basis_note?: string | null;
}

export interface CreatorPostsResponse {
  creator_id: string;
  posts: CreatorPost[];
}

export type InputBasis =
  | "full_transcript"
  | "manual_rough_transcript"
  | "caption_text"
  | "third_party_extracted_key_points"
  | "manual_summary_source_notes";

export interface CreateDemoCreatorPostRequest {
  title: string;
  content: string;
  topic: string;
  platform?: string;
  published_at?: string;
  source_url?: string;
  content_type?: "article" | "transcript" | "pasted_text";
  input_basis?: InputBasis;
  post_id?: string;
}

export interface CreateDemoCreatorPostResponse {
  post: CreatorPost;
  message: string;
  analysis_persisted: boolean;
}
