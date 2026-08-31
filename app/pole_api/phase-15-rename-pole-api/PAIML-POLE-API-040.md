# Ticket: PAIML-POLE-API-040

## Title
[Infrastructure] Rename collections `signal_histograms` → `skeleton_cohort_signals` and `skeleton_histograms` → `skeleton_video_signals`

## Description
Phase 15 (§2). Rename skeleton_data collections to reflect their function: cohort stats
(`mean`/`std` per metric and phase) and per-video histograms. Update all references
(~101 refs to `signal_histograms`): `HistogramRepository.COLLECTION_NAME`, `histogram_processor.py`
(`upsert_cohort_statistics`), queries, tests.

## What to Do (Implementation Steps)
- [ ] `app/pole_api/src/tools/repositories/histogram_repository.py`: `COLLECTION_NAME = "skeleton_video_signals"`.
- [ ] `app/pole_api/src/tools/services/histogram_service.py`: `SIGNAL_HISTOGRAMS_COLLECTION = "skeleton_cohort_signals"`.
- [ ] `app/pole_api/src/analysis/services/analyze_worker.py`: cohort collection constant → `skeleton_cohort_signals`.
- [ ] `packages/pole-train-model/src/pole_ml/processors/histogram_processor.py`: `upsert_cohort_statistics` collection name.
- [ ] Update queries, aggregations, and tests referencing `signal_histograms` / `skeleton_histograms`.
- [ ] Backfill script for legacy collections (see optional PAIML-POLE-API-042) — mark skipped if out of scope.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] No references to legacy `signal_histograms` / `skeleton_histograms` remain in code/tests.
- [ ] `skeleton_cohort_signals` and `skeleton_video_signals` created by their producer paths.
- [ ] `pixi run test-api` green (guarded `_testing` DBs).

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs; never prod).

## Dependencies
- **Blocks**: PAIML-POLE-API-041, PAIML-POLE-API-043
- **Blocked By**: PAIML-POLE-API-039

## Estimated Effort
- [M]