# Ticket: PAIML-POLA-API-008

## Title
[Application] Add `HistogramAnalysisService.submit_analysis` (background job, two-pass, error isolation)

## Description
Phase 11 (§8.3.2, §8.7 A-3/A-7/A-8). Implement the `histogram_analysis` job entry point. It submits a
monitorable job (`202` + poll) that runs the two-pass pipeline: (1) process each `video_id` with
`HistogramDataProcessor` and aggregate the cohort; (2) compute summary fields against the updated cohort
(second pass is ticket PAIML-POLA-API-011). Per-video errors are isolated (job NOT cancelled).

## What to Do (Implementation Steps)
- [ ] Step 1: Create `app/pola_api/src/tools/services/histogram_service.py` with `submit_analysis(video_ids)` → `JobRunner.submit(kind="histogram_analysis", slice_name="tools")`.
- [ ] Step 2: The runnable loops `HistogramDataProcessor.process(video_id)` per video, catching per-video exceptions into `failed`/`skipped` (job NOT cancelled).
- [ ] Step 3: Aggregate cohort `mean`/`std` into `signal_histograms` (PAIML-POLA-API-004 output) keyed by `trick_label` + `metric`.
- [ ] Step 4: Return `{processed, skipped:[{video_id,reason}], failed:[{video_id,reason}], histograms:N}` as `result_json`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `POST` submit returns `202 {job_id}`; `GET /api/tools/jobs/{id}` reaches `done`.
- [ ] One video failing does NOT fail the job; per-video reasons are surfaced.
- [ ] `result_json` matches the confirmed shape (§8.7 A-7).
- [ ] Cohort `signal_histograms` is written after the first pass.

## Integration Tests to Run (Local Verification)
- [ ] UC-91 (happy path), UC-94 (per-video error isolation).

## Dependencies
- **Blocks**: PAIML-POLA-API-009, PAIML-POLA-API-011, PAIML-POLA-API-013
- **Blocked By**: PAIML-POLA-API-003, PAIML-POLA-API-004, PAIML-POLA-API-007, PAIML-POLA-API-010

## Estimated Effort
- [L]
