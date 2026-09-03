# Ticket: PAIML-POLE-RAG-025

## Title
[Application] Unit tests for the 4 chatbot query tools

## Description
Phase 5: unit tests for the rag tool registration and handlers using a Chroma temp dir
and mocked `pole_rag` query where needed.

## What to Do (Implementation Steps)
- [ ] Step 1: Create `packages/chatbot/tests/test_rag_tools.py` (or extend existing
      `test_tools.py`).
- [ ] Step 2: Assert all 4 tools registered with expected name/params/mode/sync.
- [ ] Step 3: Assert handler returns k results (default 3) against a temp-seeded store.
- [ ] Step 4: Assert unknown DB / empty store → `ToolError` or graceful empty result.
- [ ] Step 5: Run `pixi run test-chatbot`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Unit tests pass locally (`pixi run test-chatbot`).
- [ ] Coverage for the new tool module ≥ 80%.
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] Run UC-07 unit-level: k respected, metadata present.

## Dependencies
- **Blocks**: —
- **Blocked By**: PAIML-POLE-RAG-024

## Estimated Effort
- [S]