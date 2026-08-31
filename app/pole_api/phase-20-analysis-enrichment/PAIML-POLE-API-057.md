# Ticket: PAIML-POLE-API-057

## Title
[Application] Enriched list service + controller (`GET /api/analysis/videos/summary`)

## Description
Phase 20 (§1). Wire the enriched list through the service layer and expose it as a new HTTP
endpoint. The Stitch FE Analysis History table consumes this endpoint.

## What to Do (Implementation Steps)
- [ ] Add `AnalysisService.get_enriched_list(skip, limit)` → delegates to
  `AnalysisVideoRepository.list_with_histograms(skip, limit)`.
- [ ] Add route `GET /api/analysis/videos/summary` in `analysis/controllers/videos.py`.
- [ ] Query params: `skip` (default 0), `limit` (default 50).
- [ ] Response: `200` with `List[AnalysisVideoSummary]` + `X-Total-Count` header.
- [ ] Unit tests for service + controller (mock repository).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `GET /api/analysis/videos/summary` returns enriched list with `X-Total-Count`.
- [ ] Pagination works via `skip`/`limit`.
- [ ] Unit tests pass for service + controller.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs; never prod).
- [ ] Manual: seed 3 videos (2 analyzed, 1 not) → verify response shape.

## Dependencies
- **Blocks**: PAIML-POLE-API-058
- **Blocked By**: PAIML-POLE-API-056

## Estimated Effort
- [S]
