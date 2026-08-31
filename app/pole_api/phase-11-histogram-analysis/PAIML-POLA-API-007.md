# Ticket: PAIML-POLA-API-007

## Title
[Infrastructure] Add `HistogramRepository` (Mongo `skeleton_histograms`)

## Description
Phase 11 (§8.3.2). Add the Mongo-backed repository for per-video histogram documents, keyed by
`video_id`, with idempotent upsert (delete+re-insert) and a partial `patch_phases`. Target
`settings.skeleton_db` / `skeleton_histograms` (plural). No Postgres.

## What to Do (Implementation Steps)
- [ ] Step 1: Create `app/pola_api/src/tools/repositories/histogram_repository.py`.
- [ ] Step 2: Implement `get(video_id) → doc | None` reading `settings.skeleton_db.skeleton_histograms`.
- [ ] Step 3: Implement `upsert(doc)` as delete-by-`video_id` + insert (idempotent).
- [ ] Step 4: Implement `patch_phases(video_id, phases)` as a partial `$set` on `phases.init|execution|exit.*` only.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] CRUD operations target `skeleton_histograms` in the skeleton DB; key is `video_id`.
- [ ] `upsert` is idempotent (re-running yields one doc per `video_id`).
- [ ] `patch_phases` only touches `phases.*`, never `metrics`/`resampled`.
- [ ] Lints clean; no Postgres import.

## Integration Tests to Run (Local Verification)
- [ ] UC-91 (upsert + read back), UC-92 (patch restriction), UC-93 (missing → None).

## Dependencies
- **Blocks**: PAIML-POLA-API-008, PAIML-POLA-API-009, PAIML-POLA-API-021
- **Blocked By**: —

## Estimated Effort
- [M]
