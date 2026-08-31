# Ticket: PAIML-POLA-API-031

## Title
[Application] Analyze job error isolation (no-skeleton path)

## Description
Ensure the analyze job isolates per-video failures: if no landmarks are detected, the job ends
`done` with a `failed`/`skipped` entry + reason (`no_skeleton_detected`) and leaves
`analyzed=false` — never failing the whole job with a generic error.

## What to Do (Implementation Steps)
- [ ] Detect empty/no landmark extraction and capture a structured failure reason.
- [ ] Persist the reason in `result_json.failed`/`skipped` and keep the job `done`.
- [ ] Keep `videos.analyzed=false` in the failure path.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `pixi run test-api` passes; no-skeleton path covered.

## Integration Tests to Run (Local Verification)
- [ ] UC-A4: no-skeleton video → job `done` with `no_skeleton_detected`, `analyzed=false`.

## Dependencies
- **Blocks**: PAIML-POLA-API-035
- **Blocked By**: PAIML-POLA-API-030

## Estimated Effort
- [M]
