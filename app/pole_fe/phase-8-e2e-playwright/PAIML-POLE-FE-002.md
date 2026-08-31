# Ticket: PAIML-POLE-FE-002

## Title
[Tests] E2E Workflow A (E2E-01..04) + Trick CRUD (E2E-14..15)

## Description
Implement the Workflow A and Trick CRUD scenarios from `docs/app/pole_fe/e2e-test-plan.md`.
Upload auto-embed runs **real** MediaPipe + ChromaDB (temp dir). No crawler/cutter/train stubs needed.

## What to Do (Implementation Steps)
- [ ] `e2e/workflow-a.spec.ts` — E2E-01 (create trick → 201 → DRAFT card), E2E-02 (batch upload →
      202 → poll → uploads verified), E2E-03 (verify → stats readiness true), E2E-04 (non-.mp4
      rejected, no upload created).
- [ ] `e2e/tricks-crud.spec.ts` — E2E-14 (edit → PATCH → updated), E2E-15 (delete → cascade job → 404).
- [ ] Use `request` context for seeding/DB assertions where the UI has no direct read (e.g. `stats`,
      `uploads`, `videos`); drive the UI for user-visible flows.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] All six scenarios pass against the `_testing` backend.
- [ ] DB assertions target `pole_api_testing` / `skeleton_data_testing` only.

## Integration Tests to Run (Local Verification)
- [ ] `npx playwright test e2e/workflow-a.spec.ts e2e/tricks-crud.spec.ts`.

## Dependencies
- **Blocks**: None.
- **Blocked By**: `PAIML-POLE-FE-001`.

## Estimated Effort
- [M]
