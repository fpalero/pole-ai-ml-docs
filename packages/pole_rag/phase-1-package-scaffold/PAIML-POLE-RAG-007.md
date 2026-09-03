# Ticket: PAIML-POLE-RAG-007

## Title
[Infrastructure] Wire pixi tasks for rag CLIs and tests

## Description
Phase 1: adds pixi tasks in root `pixi.toml` so the team runs everything from the
workspace root. Tasks run `python -m pole_rag.cli.*` with `cwd = "packages/rag"` and
`PYTHONPATH = "src"` (Option A layout, pole_api-style) — no console scripts, no
pyproject. Entry points are stubs until Phases 3–4 implement the modules.

## What to Do (Implementation Steps)
- [ ] Step 1: Add tasks:
      `rag-seed = { cmd = "python -m pole_rag.cli.seed", cwd = "packages/rag", env = { PYTHONPATH = "src" } }`
      (and `rag-reseed`, `rag-query`, `rag-inspect` the same way).
- [ ] Step 2: Add `test-rag = { cmd = "pytest", cwd = "packages/rag", env = { PYTHONPATH = "src" } }`.
- [ ] Step 3: Add `test-rag-live = { cmd = "pytest -m integration", cwd = "packages/rag", env = { PYTHONPATH = "src" } }`.
- [ ] Step 4: Ensure the help task list mentions the new tasks.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `pixi run test-rag` resolves and runs the (currently empty) package suite.
- [ ] CLI task names resolve to `python -m pole_rag.cli.*` commands (may fail until
      modules exist in Phase 4).
- [ ] No `[project.scripts]` anywhere for `pole_rag`; no pyproject.
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] Run UC-01/UC-05 command availability once Phase 4 lands.

## Dependencies
- **Blocks**: PAIML-POLE-RAG-021, PAIML-POLE-RAG-022
- **Blocked By**: PAIML-POLE-RAG-001, PAIML-POLE-RAG-002

## Estimated Effort
- [S]