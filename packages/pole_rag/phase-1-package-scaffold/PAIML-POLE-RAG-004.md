# Ticket: PAIML-POLE-RAG-004

## Title
[Application] Implement hash-based PDF dedupe (`dedupe.py`)

## Description
Phase 1: `dedupe_pdfs(folder) -> list[Path]` computes sha256 for every PDF in a source
folder, keeps the first file per hash (deterministic order), removes byte-identical
duplicates and logs a warning per removed file (e.g., the duplicate
`Fundamentals_of_Biomechanics_-_Nihat_Ozkaya (1).pdf` in `biomechanics/`).

## What to Do (Implementation Steps)
- [ ] Step 1: Implement `dedupe_pdfs(folder: Path) -> list[Path]` in
      `packages/pole_rag/src/pole_rag/dedupe.py`.
- [ ] Step 2: Hash each `*.pdf` with `hashlib.sha256` (streamed chunks to avoid memory
      spikes on 200 MB files).
- [ ] Step 3: Keep first file per hash (sorted by name), unlink duplicates, log warning
      with both paths; return the kept files.
- [ ] Step 4: Handle empty/missing folder (return `[]`, warn).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] The code compiles/lints without errors.
- [ ] Duplicate PDFs are removed; unique PDFs are untouched.
- [ ] Unit tests are written and passing for this specific component.
- [ ] The changes do not break existing unit tests (regression check).

## Integration Tests to Run (Local Verification)
- [ ] Run UC-03 (duplicate dedupe): seed `biomechanics/` and assert only one of the
      duplicated `Ozkaya` docs is indexed.

## Dependencies
- **Blocks**: PAIML-POLE-RAG-008, PAIML-POLE-RAG-015
- **Blocked By**: PAIML-POLE-RAG-002

## Estimated Effort
- [S]