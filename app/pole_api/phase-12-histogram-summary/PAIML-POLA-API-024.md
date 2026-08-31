# Ticket: PAIML-POLA-API-024

## Title
[Docs] Regenerate `POLE-API.md` + FE note for the summary endpoint

## Description
Phase 12 (§9.3.3). Document the new read-only summary endpoint and note the FE connection
(`docs/app/pole_analyst/fe_design.md` Summary tab: per-metric `scores`, detections/critical frame).

## What to Do (Implementation Steps)
- [ ] Step 1: Update `docs/app/pola_api/POLE-API.md` §3 index, §5 Tools, §11 note with `GET /api/tools/histograms/summary/{video_id}`.
- [ ] Step 2: Update `slices.md`/`flows.md` (summary read path).
- [ ] Step 3: Note the FE Summary tab contract (lowercase `init/execution/exit`, `scores`, `z_mean`, `detections`) in `docs/app/pole_analyst/fe_design.md`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Docs reflect the summary endpoint contract (GET-only, stored data, `404` semantics).
- [ ] FE note records the new lowercase phase names + score/detection fields.

## Integration Tests to Run (Local Verification)
- [ ] Manual review against `test_histograms_summary_api.py` contracts.

## Dependencies
- **Blocks**: —
- **Blocked By**: PAIML-POLA-API-021, PAIML-POLA-API-022

## Estimated Effort
- [S]
