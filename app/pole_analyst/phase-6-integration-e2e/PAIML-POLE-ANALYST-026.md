# Ticket: PAIML-POLE-ANALYST-026

## Title
[Test] Playwright E2E specs (upload→analyze→tabs→chat + error/empty states)

## Description
Write the E2E scenarios: upload → analyze → open Summary/Histogram/Pose/Plan tabs → chat
conversation, plus invalid-upload, empty-library, and chat-state transitions.

## What to Do (Implementation Steps)
- [ ] E2E-1: empty library → upload panel + welcome message.
- [ ] E2E-2: upload `.mp4` → card "Not analyzed".
- [ ] E2E-3: Analyze → job completes → card "Analyzed".
- [ ] E2E-4: open tabs (Summary/Histogram/Pose/Plan) render data.
- [ ] E2E-5: chat turn → state chip transitions + assistant reply.
- [ ] E2E-6: invalid upload → inline error.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] All E2E specs pass against the `_testing` backend.

## Integration Tests to Run (Local Verification)
- [ ] UC-01..07: full happy-path + edge flows verified end-to-end.

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-027
- **Blocked By**: PAIML-POLE-ANALYST-025

## Estimated Effort
- [L]
