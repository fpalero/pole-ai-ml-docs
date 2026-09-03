# Ticket: PAIML-POLE-RAG-008

## Title
[Application] Unit tests for dedupe and config

## Description
Phase 1: tests for `dedupe.py` (duplicate kept once, unique kept, hash stability) and
`config.py` (defaults, env override for `OLLAMA_HOST`).

## What to Do (Implementation Steps)
- [ ] Step 1: Create `packages/pole_rag/tests/test_dedupe.py`: two identical files → one kept
      + warning; three unique files → all kept; empty folder → `[]`.
- [ ] Step 2: Create `packages/pole_rag/tests/test_config.py`: defaults match spec;
      `OLLAMA_HOST` env override; `default_data_dir()` returns expected path.
- [ ] Step 3: Run `pixi run test-rag` (excludes `integration` marker).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Unit tests pass locally (`pixi run test-rag`).
- [ ] Coverage for both modules ≥ 80%.
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] None (pure unit).

## Dependencies
- **Blocks**: —
- **Blocked By**: PAIML-POLE-RAG-004, PAIML-POLE-RAG-005

## Estimated Effort
- [S]