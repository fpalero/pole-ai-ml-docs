# Ticket: PAIML-POLE-RAG-003

## Title
[Infrastructure] Move/copy source PDFs into `packages/pole_rag/sources/`

## Description
Phase 1: relocates the 4 resource folders from the root `rag/sources/`
(`biomechanics`, `calisthenics`, `pole`, `psicology`) into the package
`packages/pole_rag/sources/` so the package is self-contained (interview decision B).
Sources are large binaries and must be git-ignored.

## What to Do (Implementation Steps)
- [ ] Step 1: Copy (or move) `rag/sources/{biomechanics,calisthenics,pole,psicology}`
      → `packages/pole_rag/sources/`.
- [ ] Step 2: Verify all 4 folders and their PDFs are present.
- [ ] Step 3: Ensure `.gitignore` covers `packages/pole_rag/sources/` (see PAIML-POLE-RAG-006) so
      the binaries are never committed.
- [ ] Step 4: Record the original location in a `packages/pole_rag/sources/README.md` note.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] All 4 source folders exist under `packages/pole_rag/sources/` with the same files.
- [ ] `git status` shows no source PDFs staged for commit.
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] Run UC-01 / UC-03 fixture availability: `packages/pole_rag/sources/psicology/`
      contains the smallest PDF for integration tests.

## Dependencies
- **Blocks**: PAIML-POLE-RAG-016 (integration fixture source)
- **Blocked By**: —

## Estimated Effort
- [S]