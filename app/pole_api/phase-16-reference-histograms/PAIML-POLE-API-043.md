# Ticket: PAIML-POLE-API-043

## Title
[Application] `upsert_trick_histograms` + CLI/task de generación de referencias

## Description
Phase 16 (§1). Extend `HistogramDataProcessor` / `HistogramAnalysisService` with
`upsert_trick_histograms` (reuse existing resample + binning). Add a CLI/task (`pole_tools`) or
`POST /api/tools/histograms/references` trigger that aggregates reference histograms per
`(trick_label, metric, phase)` from `approved`/`accepted` clips of each trick. Update `source_count`
on regeneration and set `last_updated` timestamp.

## What to Do (Implementation Steps)

Implemented: `POST /api/tools/histograms/references` (202 job via `ToolsService.submit_reference_generation` wrapping the existing `upsert_trick_histograms` body) + query-param `GET /references?trick_label=` alias. 4 controller tests in `test_histograms_api.py` (202, missing/empty 422, empty-label 422 missing_metrics). FE-012 E2E un-skipped.

Implemented: `POST /api/tools/histograms/references` (202 job via `ReferenceGenerationService.submit_reference_generation`) wrapping the already-existing `upsert_trick_histograms` body, plus query-param `GET /references?trick_label=` alias. 4 controller-level tests in `test_histograms_api.py` cover 202 + missing/empty-body 422 + empty-label 422(missing_metrics).
- [x] Aggregate per `(trick_label, metric, phase)`; write via `TrickHistogramRepository.upsert_many`.
- [x] Set `source_count` (clips used) and `last_updated`.
- [x] Unit tests: generation from fake clip histograms, regeneration updates `source_count`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] Reference histograms generated for a given trick from its approved clips.
- [x] Regeneration updates `source_count` / `last_updated`; docs upserted (no duplicates).
- [x] `pixi run test-api` green (guarded `_testing` DBs).

## Integration Tests to Run (Local Verification)
- [x] `pixi run test-api` (guarded `_testing` DBs; never prod; histograms_api 23 passed incl. 4 new references tests).

## Dependencies
- **Blocks**: PAIML-POLE-API-044, PAIML-POLE-API-045
- **Blocked By**: PAIML-POLE-API-041

## Estimated Effort
- [M]