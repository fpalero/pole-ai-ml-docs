# Ticket: PAIML-POLE-ANALYST-015

## Title
[Application] AnalysisService — trigger analyze + job polling

## Description
Implement the analysis trigger: `POST /api/analysis/videos/{video_id}/analyze` (async job), poll
`GET /api/analysis/jobs/{job_id}` until `done`, then refresh the detail tabs and mark the card
"Analyzed" (via the `analyzed` flag).

## What to Do (Implementation Steps)
- [ ] Implement `AnalysisService.trigger(videoId)` → POST analyze.
- [ ] Poll the analysis job (2s interval, takeWhile pending/running).
- [ ] On `done`, refresh the tabs and set `analyzed=true` in the store.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `ng lint`/`ng build` pass.
- [ ] Job polling terminates on `done`/`failed` (no leak), unit-tested.

## Integration Tests to Run (Local Verification)
- [ ] UC-02: Analyze → card flips to "Analyzed" after the job completes.

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-016, PAIML-POLE-ANALYST-017, PAIML-POLE-ANALYST-018, PAIML-POLE-ANALYST-022
- **Blocked By**: PAIML-POLE-ANALYST-002

## Estimated Effort
- [M]
