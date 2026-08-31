# Ticket: PAIML-POLE-ANALYST-010

## Title
[Application] VideosService — list videos

## Description
Implement the video-library read side: `GET /api/analysis/videos` (list with the `analyzed`
flag) and thumbnail/stream URL helpers. Exposes a `VideoRecord[]` observable to the library pane.

## What to Do (Implementation Steps)
- [ ] Implement `VideosService.list()` → `GET /api/analysis/videos`.
- [ ] Map each item to a `VideoRecord` DTO (`_id`, `filename`, `analyzed`, `created_at`).
- [ ] Expose thumbnail/stream URL builders (`/api/analysis/videos/{id}/thumbnail`, `/{id}/video`).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `ng lint`/`ng build` pass.
- [ ] List mapping + URL builders are unit-tested.

## Integration Tests to Run (Local Verification)
- [ ] UC-01/UC-07: after upload, the list shows the video; empty list shows none.

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-012
- **Blocked By**: PAIML-POLE-ANALYST-002

## Estimated Effort
- [S]
