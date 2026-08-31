# Ticket: PAIML-POLE-API-058

## Title
[Testing] Enriched list integration tests + UC-B1/B2 validation

## Description
Phase 20 (§3, enriched list). Write integration tests against `analysis_db_testing` that seed
video + histogram docs and validate the enriched list endpoint end-to-end. Covers UC-B1
(happy path) and UC-B2 (mixed analyzed/unanalyzed).

## What to Do (Implementation Steps)
- [ ] Seed 3 videos in `analysis_db_testing`: 2 analyzed (with histogram docs), 1 unanalyzed.
- [ ] Test UC-B1: `GET /api/analysis/videos/summary` → `200` with 3 enriched docs, sorted by
  `created_at` desc, analyzed videos have `trick_label`/`overall_score`/`phases`.
- [ ] Test UC-B2: unanalyzed video has `trick_label: null`, `overall_score: null`, `phases: null`.
- [ ] Test pagination: `skip=1&limit=1` → returns 1 doc, `X-Total-Count: 3`.
- [ ] Test empty DB: returns `[]` with `X-Total-Count: 0`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] All 4 integration tests pass against `analysis_db_testing`.
- [ ] Tests are isolated (clean up seeded data after run).

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs; never prod).

## Dependencies
- **Blocks**: None
- **Blocked By**: PAIML-POLE-API-057

## Estimated Effort
- [S]
