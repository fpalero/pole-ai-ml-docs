# Ticket: PAIML-POLE-FE-003

## Title
[Tests] E2E Workflow B (E2E-05..12) + Workflow C (E2E-13)

## Description
Implement Workflow B and C from `docs/app/pole_fe/e2e-test-plan.md`. Crawl/cut/train use the
`E2E_FAKES` stubs (backend); extract/process/embed use real MediaPipe + ChromaDB (temp dir).

## What to Do (Implementation Steps)
- [ ] `e2e/workflow-b.spec.ts` — serial describe: E2E-05 (crawl stub → posts pending), E2E-06 (QC
      accept), E2E-07 (cut stub → clips pending), E2E-08 (clip editor accept → kind=clip), E2E-09
      (process → windows, real MediaPipe), E2E-10 (embed → Chroma temp dir), E2E-11 (train stub →
      run done), E2E-12 (approve → active).
- [ ] `e2e/workflow-c.spec.ts` — E2E-13 (retrain fine-tune stub with new class → encoder n+1).
- [ ] Seed `phase_frames` via `PUT /api/training/clips/{id}/phase-frames` before process.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Workflow B and C pass against the `E2E_FAKES=1` backend.
- [ ] No Instagram session / trained LSTM required (stubs active).

## Integration Tests to Run (Local Verification)
- [ ] `npx playwright test e2e/workflow-b.spec.ts e2e/workflow-c.spec.ts`.

## Dependencies
- **Blocks**: None.
- **Blocked By**: `PAIML-POLE-FE-001`.

## Estimated Effort
- [L]
