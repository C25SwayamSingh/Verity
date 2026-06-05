# Corroboration Engine v1 (Phase 2.6A)

Verity's corroboration engine groups similar articles into story clusters and
derives evidence-backed feed signals from source overlap.

## What it does

For each category feed:

1. Collect normalized articles from configured open providers (`fixtures`,
   `live`, `gdelt`).
2. Group related articles into **story clusters** using simple, testable logic.
3. Compute cluster-level signals:
   - source alignment / cross-source corroboration
   - source diversity
   - conservative contradiction signals
   - framing indicator
   - confidence signal
4. Return feed cards backed by cluster evidence rather than isolated article
   defaults.

## Clustering logic

Implemented in `backend/app/services/story_cluster_service.py`.

Inputs used:

- normalized headline tokens
- summary + key-claim tokens
- category match
- publication-time proximity (default 72h window)
- source/publisher identity

Matching rule (v1):

- compute headline similarity and detail similarity (token Jaccard)
- require minimum similarity threshold
- only merge into clusters in-window by time

This is intentionally transparent and deterministic. No embeddings are required
in v1.

## Cluster object

Each cluster includes:

- `cluster_id`
- `category`
- `representative_headline`
- `representative_summary`
- `articles` (refs)
- `publishers`
- `source_count`
- `independent_source_count`
- `earliest_published_at`
- `latest_published_at`
- `common_reported_details`
- `differing_details`
- `contradiction_warnings`
- `corroboration_signal`
- `source_diversity_signal`
- `confidence_signal`
- `framing_signal`
- `score_explanations`

## Signal derivation

### Corroboration signal

Based on:

- `independent_source_count`
- `source_overlap_score` (detail overlap across independent sources)

Levels:

- `strong` — broad independent coverage with high overlap
- `moderate` — several independent sources with partial overlap
- `limited` — some coverage, weak overlap
- `single_source` — effectively one independent source

### Source diversity

Derived from independent source groups, not only raw source count. Duplicate
wire-family outlets are collapsed into a canonical group when detectable.

### Contradiction signal (conservative)

Only set when explicit contradictory details are present in source metadata.
The engine does **not** infer contradictions from weak overlap alone.

### Confidence signal

A blend of:

- final score
- corroboration/credibility
- source diversity
- source overlap

Penalties:

- single-source clusters
- contradiction warnings

## Not a truth score

The engine does **not** determine absolute truth and does not prove sources right
or wrong. It estimates source alignment and corroboration from available
evidence.

## Providers in this phase

Core/open:

- `fixtures` (default)
- `gdelt` (optional, key-free)
- curated `live` RSS (optional, key-free)

Not core/required:

- Reuters API, AP API, Ground News, paid APIs, scraping pipelines

Planned optional/later (documented, not required):

- Google Fact Check Tools API, SEC EDGAR, BLS, FRED, EIA, BEA, World Bank,
  Guardian Open Platform

## Current limitations

- Lexical clustering can miss semantically similar stories with very different
  wording.
- Contradiction detection relies on explicit warning signals present in source
  records.
- No full-text article scraping in provider ingestion.
