# Ticket: PAIML-POLE-RAG-019

## Title
[Presentation] Implement `rag-query` CLI (`cli/query.py`)

## Description
Phase 4: `rag-query -o <dir> --name <db> --query "<text>" [-k 3]` queries both collections
with the shared embedder, merges results by distance ascending, prints top-k with
`source_document` (+ `image_path` for captions) and distance. Default k=3.

## What to Do (Implementation Steps)
- [ ] Step 1: Implement `main(argv=None)` in `packages/pole_rag/src/pole_rag/cli/query.py`:
      `-o/--output`, `--name` (required), `--query` (required), `-k/--k` (default
      `config.DEFAULT_K = 3`).
- [ ] Step 2: Open `ChromaStore(output_dir, name)` (read-only) and call `store.query(query, k)`.
- [ ] Step 3: Print each result: rank, distance, type (text/image), `source_document`,
      `image_path` if present, and snippet.
- [ ] Step 4: Unknown/missing DB → actionable error + exit 1.
- [ ] Step 5: Add `if __name__ == "__main__": main()`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] The code compiles/lints without errors.
- [ ] `rag-query` returns exactly k results (≤ k if store has fewer).
- [ ] Results are merged and sorted by distance.
- [ ] Unit tests are written and passing for this specific component (temp Chroma).
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] Run UC-05: `rag-query --name psicology --query "mindfulness" -k 3` → 3 items with
      metadata.

## Dependencies
- **Blocks**: PAIML-POLE-RAG-021, PAIML-POLE-RAG-024
- **Blocked By**: PAIML-POLE-RAG-014

## Estimated Effort
- [M]