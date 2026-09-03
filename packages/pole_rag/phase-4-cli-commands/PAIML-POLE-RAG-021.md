# Ticket: PAIML-POLE-RAG-021

## Title
[Infrastructure] Final pixi task wiring for CLI entry points

## Description
Phase 4: verifies the pixi tasks (PAIML-POLE-RAG-007) resolve the implemented CLI modules via
`python -m pole_rag.cli.*` with `PYTHONPATH=src`. **No `[project.scripts]`, no pyproject**
— console access comes exclusively from the root pixi tasks.

## What to Do (Implementation Steps)
- [ ] Step 1: Verify each task invokes the right module:
      `rag-seed` → `pole_rag.cli.seed`, `rag-reseed` → `pole_rag.cli.reseed`,
      `rag-query` → `pole_rag.cli.query`, `rag-inspect` → `pole_rag.cli.inspect`.
- [ ] Step 2: Confirm `cwd = "packages/rag"` and `PYTHONPATH = "src"` are set on all four
      CLI tasks; update if needed.
- [ ] Step 3: Verify `pixi run rag-seed --help`, `pixi run rag-query --help`,
      `pixi run rag-inspect --help` all work from the workspace root.
- [ ] Step 4: Confirm there is no `[project.scripts]` section anywhere for `pole_rag`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] All 4 CLI tasks executable via `pixi run <task> --help` from the root.
- [ ] No pyproject / console scripts for `pole_rag` exist.
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] Run UC-01/UC-05/UC-06 command availability end-to-end.

## Dependencies
- **Blocks**: PAIML-POLE-RAG-022
- **Blocked By**: PAIML-POLE-RAG-007, PAIML-POLE-RAG-017, PAIML-POLE-RAG-018, PAIML-POLE-RAG-019, PAIML-POLE-RAG-020

## Estimated Effort
- [S]