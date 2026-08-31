# Ticket: PAIML-POLE-ANALYST-036

## Title
[Domain/App] Servicio WS analyst + DTOs de tool calls

## Description
Phase 11 (§1, §2). App/Domain layer for the analyst chatbot UI: WebSocket client to `/ws/analyst-chat`
(frames: `connected`, `agent_reply`, `session_resumed`, `error`, relaid `job_*`), auto-reconnect +
`session_id` resume (reuse `ChatbotSocketService` from Phase 2), and tool-call DTOs
(`histogram`, `classify`, `extract_frames`, `crop`) with image artifacts.

## What to Do (Implementation Steps)
- [ ] `AnalystSocketService` connecting to `/ws/analyst-chat` (same wire protocol as `/ws/training-chat`).
- [ ] Auto-reconnect + `session_id` resume (reuse `ChatbotSocketService`).
- [ ] `ToolCallDto` (tool name, args, artifacts incl. `frame_image_path`s).
- [ ] Unit tests: connect, resume, tool-call frames.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Chat connects to `/ws/analyst-chat` with resume.
- [ ] Tool-call DTOs map artifacts (frames/images).
- [ ] `npx ng test --watch=false` green on new modules.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`.

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-037
- **Blocked By**: PAIML-POLE-API-050, PAIML-POLE-API-052, PAIML-POLE-ANALYST-035

## Estimated Effort
- [M]