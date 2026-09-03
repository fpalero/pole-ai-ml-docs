# PLAN PHASE 1 — Package scaffold, sources, dedupe, config

> **Project:** `pole_rag` · **State:** 📋 PLANNED · **Back to:** [PLAN.md](../PLAN.md)

## Scope
Create the `packages/pole_rag/` project folder, integrate it into the **root `pixi.toml`**
(no standalone pyproject — user decision), move the 4 source folders in, add hash-based
PDF dedupe, central configuration, git-ignore rules, and the pixi tasks. No
extraction/embedding logic yet.

## Tasks
- [ ] Add `pole_rag` to root `pixi.toml` `[pypi-dependencies]`: `marker-pdf` + `pillow`
      (the rest already present: chromadb, langchain-huggingface, langchain-chroma,
      langchain-text-splitters, sentence-transformers, langchain-ollama); `pixi install`.
      Docker images unaffected (Dockerfiles don't read pixi.toml).
- [ ] Create `packages/pole_rag/src/pole_rag/` source layout (Option A, pole_api-style,
      no hatchling/`__init__` ceremony) + `cli/` placeholder + `tests/` placeholder.
- [ ] Move/copy `rag/sources/{biomechanics,calisthenics,pole,psicology}` →
      `packages/pole_rag/sources/` (git-ignored).
- [ ] `dedupe.py` — `dedupe_pdfs(folder) -> list[Path]`: sha256 per file, keep first
      (sorted) per hash, delete byte-identical duplicates, warn per removed file
      (e.g., `Fundamentals_of_Biomechanics_-_Nihat_Ozkaya (1).pdf`).
- [ ] `config.py` — `DATA_DIR`, `SOURCES_DIR`, `EMBED_MODEL`
      (`sentence-transformers/all-MiniLM-L6-v2`), `EMBEDDING_DIM=384`,
      `CHUNK_SIZE=1000`, `CHUNK_OVERLAP=150`, `COLLECTION_TEXT="text_chunks"`,
      `COLLECTION_IMAGE="image_descriptions"`, `OLLAMA_MODEL="llama3.2-vision"`,
      `OLLAMA_HOST` (env, default `http://localhost:11434`), `DEFAULT_K=3`.
- [ ] `.gitignore` — add `packages/pole_rag/sources/`, `packages/pole_rag/data/`.
- [ ] Root `pixi.toml` tasks: `rag-seed`, `rag-reseed`, `rag-query`, `rag-inspect`
      (`python -m pole_rag.cli.*`, `cwd = "packages/rag"`, `env = { PYTHONPATH = "src" }`),
      `test-rag` (pytest), `test-rag-live` (pytest `-m integration`).
- [ ] Unit tests: dedupe (duplicate kept once, unique kept, hash stability),
      config defaults.

## Dependencies
None (phase 1 of the project).

## Acceptance Criteria
- `pixi install` resolves `marker-pdf` + `pillow`; no pyproject created for `pole_rag`.
- `pixi run test-rag` passes with dedupe/config tests.
- `pixi run rag-seed --help` resolves to `python -m pole_rag.cli.seed` (help text only,
  no DB work).
- Duplicate PDFs in `sources/biomechanics/` are detected by hash.
- No Dockerfile changes in the diff.

## Notes
- The docs plan/tickets live under `docs/packages/pole_rag/` (docs repo `pole-ai-ml-docs`).
- Sources/data are large binaries — never committed to git.