# Ticket: PAIML-POLE-RAG-002

## Title
[Infrastructure] Create `packages/pole_rag/src/pole_rag/` source layout (Option A)

## Description
Phase 1: creates the source layout `packages/pole_rag/src/pole_rag/` (pole_api-style, no
hatchling/`__init__` ceremony — this is not a pip package) with the `cli/` subpackage
placeholder and the `tests/` directory. Later tickets (dedupe, config, extractor,
chunker, seeder, CLIs) add modules here. Tasks run with `cwd = "packages/rag"` and
`PYTHONPATH = "src"` (see PAIML-POLE-RAG-007).

## What to Do (Implementation Steps)
- [ ] Step 1: Create `packages/pole_rag/src/pole_rag/` (no `__init__.py` required; plain modules).
- [ ] Step 2: Create `packages/pole_rag/src/pole_rag/cli/` placeholder.
- [ ] Step 3: Create `packages/pole_rag/tests/` (conftest.py placeholder).
- [ ] Step 4: Verify `PYTHONPATH=src` from `packages/pole_rag/` makes `pole_rag` importable
      (`python -c "import pole_rag"`).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `pole_rag` imports cleanly with `PYTHONPATH=src` from `packages/pole_rag/`.
- [ ] No pyproject, no hatchling config, no editable install for `pole_rag`.
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] Run UC-01 prerequisite: `pixi run rag-seed --help` resolves (after Phase 4).

## Dependencies
- **Blocks**: PAIML-POLE-RAG-004, PAIML-POLE-RAG-005, PAIML-POLE-RAG-009, PAIML-POLE-RAG-010, PAIML-POLE-RAG-015, PAIML-POLE-RAG-023
- **Blocked By**: PAIML-POLE-RAG-001

## Estimated Effort
- [S]