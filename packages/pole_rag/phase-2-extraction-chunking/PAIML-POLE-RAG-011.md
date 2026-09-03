# Ticket: PAIML-POLE-RAG-011

## Title
[Application] Unit tests for atomic table chunker

## Description
Phase 2: tests for `chunker.py` covering table atomicity, context injection, plain-text
splitting, empty input, and separator variants.

## What to Do (Implementation Steps)
- [ ] Step 1: Create `packages/pole_rag/tests/test_chunker.py`.
- [ ] Step 2: Test a multi-row `|...|` table stays in one chunk (count + content match).
- [ ] Step 3: Test context prefix (`--- CONTEXTO DE LA TABLA ---`) appears with preceding
      lines; absent when table is first.
- [ ] Step 4: Test plain paragraphs split at ~1000 chars; empty string → `[]`;
      separator variants (`|---|---|`, `| :--- |`) handled.
- [ ] Step 5: Run `pixi run test-rag`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Unit tests pass locally (`pixi run test-rag`).
- [ ] Coverage for `chunker.py` ≥ 80%.
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] None (pure unit; feeds UC-01 pipeline indirectly).

## Dependencies
- **Blocks**: —
- **Blocked By**: PAIML-POLE-RAG-010

## Estimated Effort
- [S]