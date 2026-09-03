# Ticket: PAIML-POLE-RAG-018

## Title
[Presentation] Implement `rag-reseed` CLI (`cli/reseed.py`)

## Description
Phase 4: `rag-reseed` with identical interface to `rag-seed`. Both implement full-rebuild
semantics (Option C); `reseed` is kept as a distinct, explicit command for clarity.

## What to Do (Implementation Steps)
- [ ] Step 1: Implement `main(argv=None)` in `packages/pole_rag/src/pole_rag/cli/reseed.py`
      with the same argparse contract as `rag-seed`.
- [ ] Step 2: Reuse `seed_resource` (it already rebuilds via `ChromaStore.rebuild()`);
      log "full rebuild" explicitly.
- [ ] Step 3: Same validation/exit-code behavior as `rag-seed`.
- [ ] Step 4: Add `if __name__ == "__main__": main()`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] The code compiles/lints without errors.
- [ ] `rag-reseed` exits 0 after a successful rebuild; stale entries removed (UC-02).
- [ ] Unit tests are written and passing for this specific component.
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] Run UC-02: reseed drops old docs (counts reflect only current sources).

## Dependencies
- **Blocks**: PAIML-POLE-RAG-021
- **Blocked By**: PAIML-POLE-RAG-015

## Estimated Effort
- [S]