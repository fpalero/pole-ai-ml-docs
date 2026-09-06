# Theme 04 — RAG & Retrieval · Audience: Full-Stack / Backend Engineers

> RAG as backend infrastructure: build, update, verify, and serve retrieval —
> plus indexing an entire codebase safely.

## Catalog

### D1 (adapted) — RAG Infrastructure That a Team Can Actually Maintain
- **Difficulty:** Intermediate
- **Type:** Systems guide
- **Hook:** "A RAG is a build pipeline, not a magic box — here are the CI/CD-flavored mechanics."
- **Description:** The operational RAG: source-of-truth docs, incremental writer
  (sha256 manifest) vs full regenerate, purge-on-delete, export/import
  snapshots, and query tooling (`docs-rag-read --k/--json/--extract`). Perfect
  for teams that want their docs RAG as a first-class delivery pipeline.
- **Grounding:** `docs/scripts/README.md`, `docs/scripts/rag_config.py`.
- **Sellable angle:** "RAG operations" (build/purge/reproduce) is underserved.

### D2 — Indexing a Whole Codebase Without Breaking the Build
- **Difficulty:** Intermediate
- **Type:** Practical guide
- **Hook:** "Index everything including tests, exclude nothing important, and don't ship tree-sitter to prod."
- **Description:** The code-RAG file-selection rules: included suffixes and
  tests, excluded dirs (`node_modules`, `dist`, `__pycache__`, `rag/`, cache),
  lockfile exclusion; plus the dependency-light splitter trade-off. High-value
  reference for teams building coding assistants over their own repos.
- **Grounding:** `docs/scripts/rag_code.md` / code-rag pages.
- **Sellable angle:** "Augment any repo with its own code RAG."