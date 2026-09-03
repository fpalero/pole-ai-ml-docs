# PLAN PHASE 4 — CLI commands (seed / reseed / query / inspect)

> **Project:** `pole_rag` · **State:** 📋 PLANNED · **Back to:** [PLAN.md](../PLAN.md)

## Scope
Expose the seeder + query + inspect as CLI commands via **root pixi tasks**
(`python -m pole_rag.cli.*`, `PYTHONPATH=src`) — **no `[project.scripts]`, no
pyproject**: `rag-seed`, `rag-reseed`, `rag-query`, `rag-inspect`.

## Tasks
- [ ] `cli/seed.py` — `rag-seed -i <folder> -o <dir> --name <db>`: validate args
      (input exists, name non-empty), run full rebuild seed, print per-PDF progress +
      final counts; exit 0 on success, 1 on total failure.
- [ ] `cli/reseed.py` — `rag-reseed` with identical interface (full rebuild semantics;
      implemented as the same seeder, kept as a distinct command for clarity).
- [ ] `cli/query.py` — `rag-query -o <dir> --name <db> --query "<text>" [-k 3]`:
      query both collections (same embedding), merge by distance ascending, print top-k
      with `source_document` (+ `image_path` for captions) and distance.
- [ ] `cli/inspect.py` — `rag-inspect -o <dir> [--name <db>]`: list DBs found under
      `<dir>`, per DB the two collections + counts + distinct source documents.
- [ ] Root pixi tasks verified for all 4 CLIs (`python -m pole_rag.cli.*`,
      `cwd = "packages/rag"`, `PYTHONPATH = "src"`); no `[project.scripts]` anywhere.
- [ ] Tests: argparse defaults (k=3), query merge ordering, inspect output shape;
      live CLI smoke `pixi run rag-seed --help` / `rag-query --help` / `rag-inspect
      --help`; live query against a temp-seeded DB returns exactly `k` results.

## Dependencies
Phase 3 (seeder + ChromaStore).

## Acceptance Criteria
- `pixi run test-rag` green (unit CLI tests).
- Manual smoke: seed `sources/psicology` → `data/` → `rag-inspect` shows 2 collections
  with counts → `pixi run rag-query -- --name psicology --query "mindfulness" -k 3`
  returns 3 items.
- Exit codes and error messages are actionable (missing folder, unknown DB).
- No `[project.scripts]` / pyproject for `pole_rag`.