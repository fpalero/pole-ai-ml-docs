# PAIML-DEVOPS-001 — docs-rag: `--path` filter silently returns 0 matches (chromadb 1.5.9 `$contains`)

- **Status**: 📋 PLANNED
- **Project**: dev-ops
- **Phase**: Phase 8 — docs RAG `--path` filter fix
- **Created**: 2026-09-21
- **Repo**: `fpalero/pole-ai-ml-docs` (`docs/` only — no code/scripts outside `docs/scripts/`)
- **Type**: Bug fix (docs RAG tooling)

## Context

`pixi run docs-rag-read "<query>" --path <value>` silently returns **0 matches**
even when matching chunks exist. The path filter is translated to a chromadb
metadata query using the `$contains` operator, which is not behaving as expected
on the installed chromadb version (1.5.9).

Exact location (docs repo, `docs/scripts/rag_engine.py`, function `read_query()`):

```python
# ~line 304-309
if path_filter or project_filter:
    if path_filter:
        conds.append({"path": {"$contains": path_filter}})   # <-- line 307, broken
    if project_filter:
        conds.append({"project_name": {"$eq": project_filter}})
```

- **Symptom**: `--path` filtering returns 0 results silently (no error, no
  warning), while `--project` filtering (`$eq`) works correctly.
- **Impact**: sub-agents that scope docs queries with `--path` receive empty
  results and may draw wrong conclusions. Observed in practice: the `doc`
  subagent hit this during a routine RAG refresh/verification.
- **Repro** (from workspace root `/home/fernando/Proyectos/pole-ai`):

  ```bash
  pixi run docs-rag-read "skeleton extractor" --path pole_ml --k 3
  # → 0 matches, despite chunks under paths starting with pole_ml/ existing
  pixi run docs-rag-read "skeleton extractor" --project pole_ml --k 3
  # → works (control, proves the dataset is not empty)
  ```

## Acceptance Criteria

- [ ] a. `pixi run docs-rag-read "skeleton extractor" --path pole_ml --k 3`
      returns relevant chunks (not 0).
- [ ] b. Path-filtered queries return **ONLY** files whose `path` starts with
      the given prefix (no leakage from outside the prefix).
- [ ] c. `--project` filtering still works (no regression).
- [ ] d. No behavior change to `pixi run docs-rag-write` / `pixi run
      docs-rag-generate`.

## Proposed Fix

### Option A (recommended): server-side `$eq` on `project_name` + client-side path prefix post-filter

- Keep server-side metadata filtering only for `project_name` (`$eq`, known to
  work on chromadb 1.5.9).
- Apply the path prefix filter **client-side in Python** on the returned hits:
  `hit["metadata"]["path"].startswith(path_filter)`.
- Request a larger server-side `k` to compensate for the post-filter drop, so
  the client still returns the requested number of results after filtering.
- Avoids relying on the broken/unsupported `$contains` operator entirely.

### Option B: `$eq` with full-path equality

- Switch `--path` to `{"path": {"$eq": path_filter}}` when an **exact** path is
  known.
- Does **NOT** support prefix/subdirectory matching (e.g. `pole_ml` → every
  file under `pole_ml/`), which is the common usage of `--path`. This makes it
  a fallback only.

### Note

- Before implementing, check the chromadb 1.5.9 supported metadata operators
  (e.g. via the chromadb docs / `where_document` vs `where` query syntax) — do
  **not** assume `$contains` exists or works for path strings.

## Blocks

— (none)

## Blocked By

— (none)

## Verification

Run from workspace root `/home/fernando/Proyectos/pole-ai` after the fix is
implemented in `docs/scripts/rag_engine.py`:

```bash
# a. prefix filtering returns results
pixi run docs-rag-read "skeleton extractor" --path pole_ml --k 3

# b. no leakage: every hit path starts with pole_ml/
pixi run docs-rag-read "api endpoints" --path pole_ml --k 10 --json
#   → assert all hits' metadata.path start with "pole_ml"

# c. --project filter regression check
pixi run docs-rag-read "api endpoints" --project pole_api --k 3

# d. ingestion unchanged (indexes still build/purge correctly)
pixi run docs-rag-write
pixi run docs-rag-read "docs-rag path filter contains chromadb" --k 3
```

Commit the ticket + `PROJECT_VARS.md` bump + regenerated
`docs/rag/manifests/manifest.json` (never `docs/rag/chroma/`).