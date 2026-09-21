# Ticket: PAIML-POLE-API-128

## Title
upload-dropzone spec timeout flake (501MB allocation vs 5000ms vitest timeout)

## Status
📋 PLANNED — frontend lane of phase-42 coach-gate-25.

- **Status**: 📋 PLANNED
- **Project**: pole_api (frontend lane)
- **Phase**: 42 coach-gate-25
- **Blocks**: none
- **Blocked By**: none — independent of 125/126 (BE lane); no code dependency
  on the backend regression fix (PAIML-POLE-API-127).

## Context

`app/pole_analyst/src/app/shared/components/upload-dropzone/upload-dropzone.component.spec.ts`
allocates a ~501 MB `Uint8Array` for the size-rejection tests
("guides a size rejection to 'choose a shorter video' (UC-05)" and "combines
both guidance options for a mixed format/size rejection") → **>5000 ms vitest
timeout** on the slow/contended CI runner; passes locally in ~1.3 s (25/25).
The file is untouched by recent PRs — proven flake, not a regression.

## Acceptance Criteria

1. The 2 size-rejection tests pass reliably under CI (no timeout at the default
   5000 ms).
2. All 25 tests in the spec pass; no other FE specs affected (`ng test` suite
   green).

## Proposed Fix

Pick one — prefer **A**:

- **A (preferred).** Mock `File.size` (e.g. via `Object.defineProperty` or a
  small `Blob`/`File` stub) instead of allocating a 501 MB real buffer (lines
  ~121/150/166).
- **B.** Raise the vitest timeout for this spec (e.g. `testTimeout` override) —
  acceptable but masks slowness.

## Verification

1. `npx ng test --watch=false --include=src/app/shared/components/upload-dropzone/upload-dropzone.component.spec.ts` passes (25/25).
2. Full FE checks green (`ng test` suite, no other specs affected).

## Dependencies
- **Blocked By**: none.
- **Blocks**: none.

## Estimated Effort
- [S]