# Ticket: PAIML-POLE-RAG-006

## Title
[Infrastructure] Add `.gitignore` rules for `packages/pole_rag/sources/` and `packages/pole_rag/data/`

## Description
Phase 1: prevents committing large PDF sources and generated Chroma stores. The root
`.gitignore` already ignores `**/rag/chroma/`; this ticket adds the two new package
paths.

## What to Do (Implementation Steps)
- [ ] Step 1: Edit root `.gitignore`: add `packages/pole_rag/sources/` and `packages/pole_rag/data/`.
- [ ] Step 2: Verify `git check-ignore packages/pole_rag/sources packages/pole_rag/data` returns both.
- [ ] Step 3: Confirm no PDF or chroma blob appears in `git status`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Both paths are ignored by git.
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] None (repo hygiene).

## Dependencies
- **Blocks**: PAIML-POLE-RAG-003 (sources safety)
- **Blocked By**: —

## Estimated Effort
- [S]