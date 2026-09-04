# Ticket: PAIML-POLE-RAG-027

## Title
[Infrastructure] Ship `pole_rag` in the pole-api base image (COPY + import path)

## Description
Phase 6, step 1 of 4. The staging pole-api pod cannot import `pole_rag`
(`ModuleNotFoundError`; live-pod verified). `app/pole_api/docker/base.Dockerfile`
copies six packages but not `packages/pole_rag`, and the thin `Dockerfile` only
layers `app/pole_api/*` with `PYTHONPATH=/app/src`. Until this ticket lands, the
4 chatbot tools (`query_pole`, `query_calisthenics`, `query_psicology`,
`query_biomechanics`) raise `ToolError` on every call. This ticket makes
`pole_rag` importable in the image without touching `/data/chroma`.

## Repository
pole-ai-ml

## What to Do (Implementation Steps)
- [ ] Step 1 [pole-ai-ml]: In `app/pole_api/docker/base.Dockerfile`, add
      `COPY packages/pole_rag ./packages/pole_rag` alongside the existing six
      `COPY packages/*` lines (build stage, `WORKDIR /workspace`).
- [ ] Step 2 [pole-ai-ml]: Make `pole_rag` importable at runtime. `pole_rag` has
      no `pyproject.toml` (user decision, Phase 1) so it cannot be
      `pip install`ed: extend the runtime `PYTHONPATH` to include the package
      `src` (e.g. `ENV PYTHONPATH="/app/src:/app/packages/pole_rag/src"` or a
      `COPY packages/pole_rag/src/pole_rag` into the venv site-packages path —
      pick one lane and document it). Verify `python -c "import pole_rag.config"`.
- [ ] Step 3 [pole-ai-ml]: If the embedder-bake lane is chosen (see ticket 029),
      add `sentence-transformers` + `all-MiniLM-L6-v2` pre-download to this same
      base layer so the slow rebuild happens once, not twice.
- [ ] Step 4 [pole-ai-ml]: Rebuild the **base** image lane
      (`base.Dockerfile`, content-hashed tag) — explicitly NOT the thin app
      `Dockerfile` lane — and note the new base tag in the ticket. Confirm the
      thin app image still builds `FROM` it in seconds.
- [ ] Step 5 [pole-ai-ml]: Smoke-test locally: `docker run <base> python -c
      "from pole_rag import config; print(config.default_data_dir())"` passes;
      `python -c "import pole_chatbot.rag_tools"` no longer raises
      `ModuleNotFoundError` (it may raise `ToolError` for missing DBs — that is
      correct until ticket 029 seeds).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `base.Dockerfile` contains a `pole_rag` COPY line; no other package COPY
      removed.
- [ ] `import pole_rag.config` succeeds inside the built base image.
- [ ] Thin app `Dockerfile` unchanged except the `BASE_IMAGE` arg bump (if any).
- [ ] `/data/chroma` handling untouched (no migration, no path change).
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] Image smoke: `import pole_rag` + `rag_tools` import without
      `ModuleNotFoundError`; missing-DB call still maps to `ToolError`.

## Dependencies
- **Blocks**: PAIML-POLE-RAG-028
- **Blocked By**: —

## Estimated Effort
- [M]
