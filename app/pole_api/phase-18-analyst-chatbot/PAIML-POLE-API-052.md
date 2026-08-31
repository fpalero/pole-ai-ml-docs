# Ticket: PAIML-POLE-API-052

## Status
✅ DONE — Implemented

## Title
[Infrastructure] Relaying de job events del análisis al WS + resume de sesiones

## Description
Phase 18 (§3). Relay analysis pipeline job events to the WS so the FE synchronizes the progress panel
(stages Extraction→Processing→Phase detection→Classification & analysis→Summary). Session resume after
reconnect.

## What to Do (Implementation Steps)
- [x] Subscribe to job events (`job_started`, `job_progress`, `job_done`, `job_error`) and relay to the analyst WS.
- [x] Map 5-stage pipeline progress to relaid frames.
- [x] Resume: `session_resumed` with prior context after reconnect.
- [x] Integration tests: job events relaid; resume restores session.

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] Job events relaid over `/ws/analyst-chat`; FE progress panel syncable.
- [x] Session resume works after reconnect.
- [x] `pixi run test-api` green (guarded `_testing` DBs).

## Integration Tests to Run (Local Verification)
- [x] `pixi run test-api` (guarded `_testing` DBs; never prod).

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-036, PAIML-POLE-ANALYST-037
- **Blocked By**: PAIML-POLE-API-050, PAIML-POLE-API-051

## Estimated Effort
- [M]