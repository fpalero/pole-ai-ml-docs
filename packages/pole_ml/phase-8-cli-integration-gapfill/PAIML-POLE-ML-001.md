# Ticket: PAIML-POLE-ML-001

## Title
[Tests] CLI integration gap-fill — idempotent re-run + `--phase-frames` skip path

## Description
`packages/pole-train-model/tests/test_cli_integration.py` (commit `a830cf1`) covers the
extract→process happy path and process-without-extract error, but the documented UC-82..90 CLI
matrix (see `docs/app/pola_agent/implementation_plan.md` §12.9.3) also requires idempotent re-run and
the `--phase-frames` skip path. Fill those gaps using the existing fixtures.

## What to Do (Implementation Steps)
- [ ] Reuse `_pick_video`, `_run_cli`, `_cleanup` (do NOT duplicate them).
- [ ] Add `test_process_cli_rerun_is_idempotent`: extract → process → process again → assert the
      windows/histogram count is unchanged (delete+re-insert, no duplicates).
- [ ] Add `test_process_cli_skips_histogram_without_phase_frames`: seed a clip **without**
      `phase_frames`, extract, process → assert `skeleton_histograms` has no doc for the clip (or the
      clip is skipped with a clear reason) while `skeleton_windows` still land.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] New tests pass against `pole_api_testing` / `skeleton_data_testing` (real Mongo + real source video).
- [ ] No fixture duplication; existing `_pick_video`/`_run_cli`/`_cleanup` reused.
- [ ] `pixi run test` (pole-train-model) stays ≥80% coverage.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test` green (includes `test_cli_integration.py`).

## Dependencies
- **Blocks**: None.
- **Blocked By**: None.

## Estimated Effort
- [S]
