# Ticket: PAIML-POLA-API-020

## Title
[Docs] Regenerate `POLE-API.md` + `slices.md`/`flows.md` for Phase 11

## Description
Phase 11 (§8.3.5 bullet 4). After implementation, regenerate the API docs to reflect the new histogram
endpoints and the removed reference/threshold/attempt/analyze surface.

## What to Do (Implementation Steps)
- [ ] Step 1: Update `docs/app/pola_api/POLE-API.md` §3 endpoint index, §5 Tools, §10 metrics, §11 note.
- [ ] Step 2: Update `docs/app/pola_api/slices.md` and `flows.md` to drop the removed endpoints and add the histogram namespace.
- [ ] Step 3: Ensure the 8-metric set and `signal_histograms` collection are documented.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Docs accurately describe `POST/GET/PATCH /api/tools/histograms/*` and the jobs router.
- [ ] No reference/threshold/attempt/analyze endpoints remain documented.

## Integration Tests to Run (Local Verification)
- [ ] Manual review against `test_histograms_api.py` contracts.

## Dependencies
- **Blocks**: —
- **Blocked By**: PAIML-POLA-API-013, PAIML-POLA-API-015

## Estimated Effort
- [S]
