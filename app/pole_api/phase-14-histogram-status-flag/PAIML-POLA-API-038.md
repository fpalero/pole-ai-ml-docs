# Ticket: PAIML-POLA-API-038

## Title
[Tests] Flag writes (both paths) + clip-scoped `extracted`/`histo` counts

## Description
Phase 14 (§10.3.3). Add API/integration coverage for PAIML-POLA-API-036 and PAIML-POLA-API-037,
targeting `pole_api_testing` / `skeleton_data_testing` (guarded `_testing` suffix). Assert the
`histogram_processed` flag flips on both producer paths, stays `false` for skipped videos, and that
`count_by_status`/`list_videos` return clip-scoped `extracted`/`histo` counts.

## What to Do (Implementation Steps)
- [ ] `app/pola_api/tests/tools/test_histograms_api.py`: after `POST /api/tools/histograms/analysis`
      reaches `done`, assert `videos[A].histogram_processed=true` for processed A and unchanged for
      skipped B (UC-100).
- [ ] `app/pola_api/tests/training/test_process_integration.py`: after a successful `/process`
      (both processors), assert `videos[A].histogram_processed=true`; a clip with missing
      `phase_frames` stays unflagged and lands in `result_json.skipped` (UC-99).
- [ ] `app/pola_api/tests/training/test_video_repository.py` (or `test_process*.py`): assert
      `count_by_status(class_id, clip=True/False/None)` returns correct `extracted`/`histo` buckets and
      that the default `clip=None` preserves legacy buckets.
- [ ] Add `X-Count-extracted` / `X-Count-histo` header assertions on the `?clip=true` listing.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] UC-99, UC-100, UC-101 covered; existing `test_process.py` / `test_histograms_api.py` stay green.
- [ ] ≥80% coverage on `app/pola_api` measured via `pixi run test-api`.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs; never prod).

## Dependencies
- **Blocks**: None
- **Blocked By**: PAIML-POLA-API-036, PAIML-POLA-API-037

## Estimated Effort
- [M]
