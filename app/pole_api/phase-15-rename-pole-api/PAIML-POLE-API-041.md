# Ticket: PAIML-POLE-API-041

## Title
[Domain] Create `skeleton_trick_histograms` collection + model + repo

## Description
Phase 15 (§3). New reference-histogram collection. One document per `(trick_label, metric, phase)`
with `trick_label`, `metric`, `phase` (ENTRADA/EJECUCIÓN/SALIDA), `bins`, `counts`, `total`,
`last_updated`, `source_count` (number of clips used). Produced by Phase 16 (reference generation),
consumed by Phase 17 (phase detection).

## What to Do (Implementation Steps)
- [ ] Define `TrickHistogram` model (fields above) with pydantic validation.
- [ ] Add `TrickHistogramRepository` with `upsert_many`, `find_by_trick(metric?)`, `delete_by_trick`, `count_by_trick`.
- [ ] Index `(trick_label, metric, phase)` unique; wire collection name constant `skeleton_trick_histograms`.
- [ ] Unit tests for model + repository.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Collection `skeleton_trick_histograms` created with unique compound index.
- [ ] Repository CRUD + count covered by unit tests.
- [ ] `pixi run test-api` green (guarded `_testing` DBs).

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs; never prod).

## Dependencies
- **Blocks**: PAIML-POLE-API-043, PAIML-POLE-API-044, PAIML-POLE-API-046
- **Blocked By**: PAIML-POLE-API-039, PAIML-POLE-API-040

## Estimated Effort
- [S]