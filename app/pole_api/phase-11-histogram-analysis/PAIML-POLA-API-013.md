# Ticket: PAIML-POLA-API-013

## Title
[Presentation] Add `controllers/histograms.py` (POST analysis, GET, PATCH)

## Description
Phase 11 (§8.3.3). Create the REST controller for the `/api/tools/histograms/` namespace:
`POST analysis` (202), `GET {video_id}` (full doc), `PATCH {video_id}` (phases only).

## What to Do (Implementation Steps)
- [ ] Step 1: Create `app/pola_api/src/tools/controllers/histograms.py`.
- [ ] Step 2: `POST /api/tools/histograms/analysis` → `202 {job_id}` (body `{video_ids: [str]}`).
- [ ] Step 3: `GET /api/tools/histograms/{video_id}` → `200` full doc / `404` missing.
- [ ] Step 4: `PATCH /api/tools/histograms/{video_id}` → `200` updated / `404` missing / `422` on any non-phase field.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Endpoints respond with the documented codes and payload shapes.
- [ ] `PATCH` rejects `metrics/resampled` (and any non-`phases` field) with `422`.
- [ ] `404` when the histogram doc is missing.

## Integration Tests to Run (Local Verification)
- [ ] UC-91 (POST→poll→GET), UC-92 (PATCH 422), UC-93 (GET/PATCH 404).

## Dependencies
- **Blocks**: PAIML-POLA-API-014, PAIML-POLA-API-019, PAIML-POLA-API-020
- **Blocked By**: PAIML-POLA-API-008, PAIML-POLA-API-009, PAIML-POLA-API-011, PAIML-POLA-API-012

## Estimated Effort
- [M]
