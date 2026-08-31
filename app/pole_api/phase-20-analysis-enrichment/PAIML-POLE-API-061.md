# Ticket: PAIML-POLE-API-061

## Title
[Documentation] Update POLE-API.md with new endpoints + cross-ticket regression test

## Description
Phase 20 (§3). Update the API documentation with the two new endpoints and run a final regression
test across all Phase 20 tickets to ensure nothing is broken.

## What to Do (Implementation Steps)
- [ ] Update `docs/app/pola_api/POLE-API.md` (or `slices.md`) with:
  - `GET /api/analysis/videos/summary` — description, query params, response shape, example.
  - `GET /api/analysis/videos/{video_id}/pose/frames` — description, response shape, 404 case.
- [ ] Run full `pixi run test-api` suite to confirm no regressions across all analysis endpoints.
- [ ] Verify both new endpoints work with `curl` against running API (manual smoke test).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] POLE-API.md documents both new endpoints with accurate response shapes.
- [ ] `pixi run test-api` passes with no regressions.
- [ ] Manual smoke test confirms both endpoints return correct data.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (full suite, guarded `_testing` DBs; never prod).
- [ ] Manual `curl` smoke test against running API.

## Dependencies
- **Blocks**: None (final ticket in Phase 20)
- **Blocked By**: PAIML-POLE-API-058, PAIML-POLE-API-060

## Estimated Effort
- [S]
