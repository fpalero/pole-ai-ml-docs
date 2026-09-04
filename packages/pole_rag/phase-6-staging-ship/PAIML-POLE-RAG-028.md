# Ticket: PAIML-POLE-RAG-028

## Title
[Application] `POLE_RAG_DATA_DIR` env override in `pole_rag` config

## Description
Phase 6, step 2 of 4. `pole_rag/config.default_data_dir()` currently returns
`PACKAGE_ROOT / "data"` with no env hook, so staging cannot point the chatbot
tools at `/data/rag` without code edits. This ticket adds the override; the
Helm value that sets it on staging lives in ticket 029 (repo
`pole-ai-ml-infra`) and is NOT touched here.

## Repository
pole-ai-ml

## What to Do (Implementation Steps)
- [ ] Step 1 [pole-ai-ml]: In `packages/pole_rag/src/pole_rag/config.py`, read
      `POLE_RAG_DATA_DIR` from the environment in `default_data_dir()` (and the
      `DATA_DIR` constant if it is module-level): when the env var is set and
      non-empty, return `Path(os.environ["POLE_RAG_DATA_DIR"])`; otherwise return
      `PACKAGE_ROOT / "data"` exactly as today.
- [ ] Step 2 [pole-ai-ml]: Keep `SOURCES_DIR`, `EMBED_MODEL`
      (`sentence-transformers/all-MiniLM-L6-v2`), `CHUNK_SIZE=1000`,
      `CHUNK_OVERLAP=150`, collection names, `OLLAMA_*`, `DEFAULT_K=3`
      unchanged.
- [ ] Step 3 [pole-ai-ml]: Thread the override through `ChromaStore`/`query`/`cli`
      call sites that currently use the hardcoded default, so `query_*` tools
      with no explicit `data_dir` honour the env var (explicit `data_dir`
      argument still wins).
- [ ] Step 4 [pole-ai-ml]: Add/extend unit tests in
      `packages/pole_rag/tests/test_config.py`: env set → returns env path; env
      unset/empty → returns package `data/`; `query` with env set resolves
      against it. Run `pixi run test-rag`.
- [ ] Step 5 [pole-ai-ml]: Document the variable in the ticket and in
      `packages/pole_rag/sources/README.md` if it documents config (one line:
      `POLE_RAG_DATA_DIR` overrides the data dir; staging sets `/data/rag` via
      Helm in ticket 029).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `POLE_RAG_DATA_DIR=/tmp/x python -c "from pole_rag.config import
      default_data_dir; print(default_data_dir())"` prints `/tmp/x`.
- [ ] Env unset prints `<package>/data` (previous behaviour preserved).
- [ ] `pixi run test-rag` green; coverage for `config.py` ≥ 80%.
- [ ] No Helm/chart file modified in this ticket (staging value is 029).
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] UC-05/UC-07 read path: `rag-query -o $POLE_RAG_DATA_DIR --name pole
      --query "..."` resolves via env when `-o` is omitted (if supported) or
      explicitly passed.

## Dependencies
- **Blocks**: PAIML-POLE-RAG-029
- **Blocked By**: PAIML-POLE-RAG-027

## Estimated Effort
- [S]
