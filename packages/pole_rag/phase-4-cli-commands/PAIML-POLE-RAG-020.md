# Ticket: PAIML-POLE-RAG-020

## Title
[Presentation] Implement `rag-inspect` CLI (`cli/inspect.py`)

## Description
Phase 4: `rag-inspect -o <dir> [--name <db>]` lists DBs found under the output dir and,
per DB, the two collections, entry counts, and distinct source documents.

## What to Do (Implementation Steps)
- [ ] Step 1: Implement `main(argv=None)` in `packages/pole_rag/src/pole_rag/cli/inspect.py`:
      `-o/--output` (required), `--name` (optional filter).
- [ ] Step 2: Enumerate subdirectories of the output dir containing a Chroma DB
      (e.g., `chroma.sqlite3` present); if `--name` given, restrict to it.
- [ ] Step 3: For each DB, open `ChromaStore`, print `counts()` and `list_sources()`.
- [ ] Step 4: No DBs found → informative message, exit 0.
- [ ] Step 5: Add `if __name__ == "__main__": main()`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] The code compiles/lints without errors.
- [ ] `rag-inspect` output lists DBs, collections, counts, and source docs.
- [ ] Unit tests are written and passing for this specific component (temp Chroma).
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] Run UC-06: after a live seed, `rag-inspect -o <temp>` shows expected counts.

## Dependencies
- **Blocks**: PAIML-POLE-RAG-021
- **Blocked By**: PAIML-POLE-RAG-014

## Estimated Effort
- [S]