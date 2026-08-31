# Ticket: PAIML-POLE-ANALYST-023

## Title
[Infrastructure] Reconnect keeps session + analysis-in-progress placeholders

## Description
Harden the WS reconnect so the `session_id` is preserved across drops, and show skeleton
placeholders (loading cards) while `ChatState` is `Working` (analysis in progress), synced to the
chat state.

## What to Do (Implementation Steps)
- [ ] Ensure reconnect resumes with the stored `session_id` (verify PAIML-POLE-ANALYST-006).
- [ ] Render skeleton placeholders in the detail tabs while `ChatState === Working`.
- [ ] Sync placeholders with the `job_started`/`job_progress` frames.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `ng lint`/`ng build` pass.
- [ ] Reconnect resumes the session; placeholders show during Working and clear on Completed.

## Integration Tests to Run (Local Verification)
- [ ] UC-04: reconnect mid-analysis resumes and placeholders resolve on completion.

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-024
- **Blocked By**: PAIML-POLE-ANALYST-006

## Estimated Effort
- [M]
