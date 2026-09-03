# Ticket: PAIML-POLE-RAG-001

## Title
[Infrastructure] Add `pole_rag` project to root `pixi.toml` (dev deps, no standalone pyproject)

## Description
First ticket of the `pole_rag` project (Phase 1). Per user decision, `pole_rag` has **no
standalone `pyproject.toml`** — it is integrated into the root `pixi.toml` (the
`app/pole_api` pattern). The root pixi already provides `chromadb`,
`langchain-huggingface`, `langchain-chroma`, `langchain-text-splitters`,
`sentence-transformers`, `langchain-ollama`. Only `marker-pdf` (PDF→Markdown) and
`pillow` (image handling) are new. **Docker images are unaffected** — they do not read
pixi.toml (see `app/pole_api/docker/base.Dockerfile`), so Marker never enters the API
image.

## What to Do (Implementation Steps)
- [ ] Step 1: Create the project folder `packages/pole_rag/` (with `src/`, `sources/`, `data/`
      as later tickets create them).
- [ ] Step 2: Add to root `pixi.toml` `[pypi-dependencies]`: `marker-pdf = ">=1,<2"` and
      `pillow = ">=10.4.0,<12"` (verify latest compatible versions).
- [ ] Step 3: Run `pixi install` and confirm the env resolves with the new deps.
- [ ] Step 4: Verify no pyproject is created for `pole_rag`; confirm `pixi run` still works for
      existing tasks (regression).
- [ ] Step 5: Confirm Docker images are untouched (`git status` shows no Dockerfile changes).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `pixi install` resolves the new deps without conflicts.
- [ ] `marker` and `PIL` are importable in the pixi env.
- [ ] No `packages/pole_rag/pyproject.toml` exists; no Dockerfile modified.
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] Run UC-01 prerequisite: env has Marker available for the seeder (verified in Phase 3).

## Dependencies
- **Blocks**: PAIML-POLE-RAG-002, PAIML-POLE-RAG-003, PAIML-POLE-RAG-007, PAIML-POLE-RAG-009, PAIML-POLE-RAG-012, PAIML-POLE-RAG-013, PAIML-POLE-RAG-014
- **Blocked By**: —

## Estimated Effort
- [S]