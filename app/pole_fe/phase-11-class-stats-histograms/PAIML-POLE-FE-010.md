# Ticket: PAIML-POLE-FE-010

## Title
[Presentation] Action "Generate reference histograms" + selector de videos + job progress

## Description
Phase 11 (§1). On the trick detail page: "Generate reference histograms" action with video selector
(reusing the existing video-grid selection). `POST /api/tools/histograms/references` with
`{trick_label, video_ids}` → 202 `{job_id}` → poll `GET /api/tools/jobs/{job_id}` (reuse `jobs-store`).

## What to Do (Implementation Steps)
- [ ] Add "Generate reference histograms" action to trick detail (video selection from existing grid selection).
- [ ] Call `generateReferences`; on 202 poll the job via `JobPollingService` (existing `jobs-store`).
- [ ] Show job progress (pending/running/done/failed) + `skipped` videos without `phase_frames`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] User selects videos and generates reference histograms (202 + poll to done).
- [ ] `skipped` videos (no `phase_frames`) surfaced from the job result.
- [ ] Unit tests cover the new action + progress wiring.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`.

## Dependencies
- **Blocks**: PAIML-POLE-FE-012
- **Blocked By**: PAIML-POLE-FE-009

## Estimated Effort
- [M]