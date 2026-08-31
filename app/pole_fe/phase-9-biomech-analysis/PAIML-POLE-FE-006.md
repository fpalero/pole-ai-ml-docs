# Ticket: PAIML-POLE-FE-006

## Title
[Presentation] Extract / Biomech / Histo bulk actions + EXTRACTED / HISTO filter statuses

## Description
The Stitch `fe_pole` update adds three pipeline steps to the trick-detail bulk toolbar
(`Extract`, `Biomech`, `Histo`) and two clip filter statuses (`EXTRACTED`, `HISTO`), on top of the
existing `Process` / `Embed` / `CROP` / `Delete`. Wire them to the existing `pola_api` endpoints
(see `PLAN.md` §3 Phase 9 mapping) and add the status pills + counts.

- **Extract** → `POST /api/training/classes/{id}/extract` (202 job; poll via `JobPollingService`).
- **Biomech** → `POST /api/training/classes/{id}/process` (biometric windows).
- **Histo** → `POST /api/tools/histograms/analysis` (histogram + summary).
- **EXTRACTED** status ← `video.extracted` flag (already returned by the list endpoint).
- **HISTO** status ← `video.histogram_processed` flag + filter counts from the `X-Count-extracted` /
  `X-Count-histo` headers (provided by `pola_api` Phase 14 — `PAIML-POLA-API-037`). **No per-clip N+1**
  (Q1 resolution, `PLAN.md` §3 Phase 9).

## What to Do (Implementation Steps)
- [ ] In `trick-detail.page.ts` clips bulk bar, add `Extract` (`accessibility_new`),
      `Biomech` (`auto_fix_high`), `Histo` (`bar_chart`) buttons (clips-only, like `Process`),
      each opening a lightweight confirm + submitting the corresponding service call and polling the
      returned job via `JobPollingService`.
- [ ] Extend `videoFilters` with `extracted` and `histo`; update `filteredClips()` /
      `clipFilterCount()` to filter on the `extracted` and `histogram_processed` card flags; read the
      pill counts from the `X-Count-*` counts the list request already returns (no N+1).
- [ ] Extend `VideoCardModel.statusLabel` / status pills to render `EXTRACTED` (from `extracted`)
      and `HISTO` (from `histogram_processed`) states, following the existing `pending/processed/ready`
      pill styling.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Selecting clips and clicking `Extract`/`Biomech`/`Histo` submits the right endpoint with
      `{video_ids}` and polls the job to completion; success/error toasts shown.
- [ ] `EXTRACTED` and `HISTO` pills + filter counts render correctly against `_testing` DBs.
- [ ] Unit tests cover the new bulk handlers and filter/count logic (≥80% on touched files).

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`.

## Dependencies
- **Blocks**: `PAIML-POLE-FE-008`.
- **Blocked By**: `PAIML-POLE-FE-005`, `PAIML-POLA-API-037` (`X-Count-extracted`/`X-Count-histo`).

## Estimated Effort
- [M]
