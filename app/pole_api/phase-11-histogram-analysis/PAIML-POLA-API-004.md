# Ticket: PAIML-POLA-API-004

## Title
[Application] Add cohort `mean`/`std` statistics to `signal_histograms`

## Description
Phase 11 (§8.3.1, §8.7 A-4). Cohort statistics are stored in a **separate**
`signal_histograms` collection — **one doc per `(trick_label, metric)`** with **300-pt** `mean`/`std`
arrays (sample std `ddof=1`) and embedded `phase_bounds`. These feed both Phase 11's second pass
(z-scores) and Phase 12's summary read.

## What to Do (Implementation Steps)
- [ ] Step 1: Add a helper in `pole_ml` (processor or a small service) that, given a list of 300-pt resampled curves for a `(trick_label, metric)`, computes element-wise `mean` and `std` (`ddof=1`).
- [ ] Step 2: Write/upsert one document per `(trick_label, metric)` into `skeleton_data.signal_histograms` with fields `{trick_label, metric, mean, std, count, phase_bounds, generated_at}`.
- [ ] Step 3: `phase_bounds = {init: [0,99], execution: [100,199], exit: [200,299]}`.
- [ ] Step 4: Keep `mean`/`std` OUT of the per-video `skeleton_histograms` doc (cohort-level only).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `signal_histograms` contains one doc per `(trick_label, metric)` for all 8 metrics after processing.
- [ ] `mean`/`std` are 300-pt arrays; `std` uses `ddof=1` (sample).
- [ ] `count` reflects the number of videos in the cohort; `phase_bounds` is correct.
- [ ] No cohort stats leak into the per-video document.

## Integration Tests to Run (Local Verification)
- [ ] UC-91 — after analysis, assert `signal_histograms` docs exist per `(trick_label, metric)` with 300-pt `mean`/`std`.

## Dependencies
- **Blocks**: PAIML-POLA-API-006, PAIML-POLA-API-008, PAIML-POLA-API-011
- **Blocked By**: PAIML-POLA-API-002, PAIML-POLA-API-003

## Estimated Effort
- [M]
