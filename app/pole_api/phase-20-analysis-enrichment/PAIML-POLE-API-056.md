# Ticket: PAIML-POLE-API-056

## Title
[Domain] Enriched analysis list schema + repository (`AnalysisVideoSummary` + Mongo aggregation)

## Description
Phase 20 (§1). Create the Pydantic model and repository method for the enriched analysis list
endpoint. This joins `analysis-db.videos` with `analysis-db.video_histograms` to return per-video
summary data (trick_label, overall_score, phases) in a single query. The Stitch design needs this
for the Analysis History table.

## What to Do (Implementation Steps)
- [ ] Add `AnalysisVideoSummary` Pydantic model to `analysis/schemas.py` with fields:
  `_id`, `filename`, `analyzed`, `trick_label` (optional), `overall_score` (optional 0-100),
  `phases` (optional: `init`, `execution`, `exit` each with `start`/`end`), `created_at`.
- [ ] Add `AnalysisVideoRepository.list_with_histograms(skip, limit)` method — Mongo aggregation
  pipeline joining `videos` with `video_histograms` on `video_id`/`_id`.
- [ ] Pipeline stages: `$lookup` (videos → video_histograms), `$unwind` (nullable), `$project`
  (reshape to `AnalysisVideoSummary`), `$sort` (`created_at` desc), `$skip`/`$limit`.
- [ ] Handle unanalyzed videos: `trick_label: null`, `overall_score: null`, `phases: null`.
- [ ] Unit tests for the aggregation pipeline (mock Mongo).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `AnalysisVideoSummary` model exists with all fields and validation.
- [ ] `list_with_histograms()` returns enriched docs sorted by `created_at` desc.
- [ ] Unanalyzed videos have null fields for trick/score/phases.
- [ ] Unit tests pass for model + repository.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs; never prod).

## Dependencies
- **Blocks**: PAIML-POLE-API-057, PAIML-POLE-API-058
- **Blocked By**: None (Phase 13 analysis slice is done)

## Estimated Effort
- [M]
