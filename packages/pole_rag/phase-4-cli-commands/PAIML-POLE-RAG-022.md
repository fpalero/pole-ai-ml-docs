# Ticket: PAIML-POLE-RAG-022

## Title
[Application] CLI tests: arg parsing, merge order, inspect output + live query smoke

## Description
Phase 4: unit tests for the CLI modules (arg parsing, k default, merge order, inspect
shape) plus a live query smoke against a temp-seeded DB.

## What to Do (Implementation Steps)
- [ ] Step 1: Create `packages/pole_rag/tests/test_cli_seed.py`, `test_cli_query.py`,
      `test_cli_inspect.py` (unit; mock `seed_resource`/`ChromaStore`).
- [ ] Step 2: Assert `-k` defaults to 3; invalid `--name`/missing `--query` → exit 1.
- [ ] Step 3: Assert query results merged and sorted by distance (ascending).
- [ ] Step 4: Assert inspect output contains DB name, collection names, counts, sources.
- [ ] Step 5: Live smoke (marked `integration`): seed a temp DB, `rag-query -k 3` returns
      3 items (UC-05).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Unit tests pass locally (`pixi run test-rag`).
- [ ] Live smoke passes via `pixi run test-rag-live`.
- [ ] Coverage for CLI modules ≥ 80%.
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] Run UC-05 live: exactly k=3 merged results.

## Dependencies
- **Blocks**: —
- **Blocked By**: PAIML-POLE-RAG-021

## Estimated Effort
- [M]