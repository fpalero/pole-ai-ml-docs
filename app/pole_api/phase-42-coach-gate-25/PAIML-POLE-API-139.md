# Ticket: PAIML-POLE-API-139

## Title
Implement `overall_score` computation + persistence (summary join reads None today)

- **Status**: 📋 PLANNED
- **Project**: pole_api (analysis histograms + summary)
- **Phase**: 42 coach-gate-25
- **Blocks**: —
- **Blocked By**: — independent of 138 (backfills 138's fresh histograms when both land, but neither blocks the other).

## Context

Evidence (binding): **zero writers repo-wide** (`grep overall_score=` empty);
histograms carry `scores` / `z_mean` / `phase_scores` but **no
`overall_score`**; the summary join reads `$histogram.overall_score` → always
None → harness numeric-score filter + readiness evidence fail.

USER DECISIONS (binding): NO mock data — the fix must compute from real
`scores` on real histograms (138's training-seeding run is the live source),
persist on the histogram doc, and backfill existing scored histograms.

## Scope

1. **Define formula** (recommend: **mean of metric scores**, document weighting
   choice in code + ticket close note — e.g. plain mean vs weighted by metric;
   record why).
2. **Write on histogram doc at analysis completion (worker)**: compute +
   persist `overall_score` whenever a scored histogram is finalized.
3. **Backfill existing scored histograms**: one-shot migration/script for docs
   that have `scores` but no `overall_score`.
4. **Unit tests (formula edge cases)**: empty scores → **None, not 0**;
   single-score, multi-score mean, and None-propagation cases.

Out of scope: changing the summary join shape (it already reads the field —
this ticket makes the field real).

## Validation Plan

1. `rg "overall_score\s*=" app/` → writer exists (worker + backfill).
2. Unit tests: `pytest -k overall_score` green (empty → None, mean cases).
3. Manual: scored video → histogram doc has numeric `overall_score`;
   `GET` summary returns the same numeric value.
4. Harness discovery numeric-score filter passes on a scored video.

## Acceptance Criteria

- [ ] `overall_score` formula defined + weighting choice documented.
- [ ] Worker writes numeric `overall_score` on histogram at analysis completion.
- [ ] Backfill covers existing scored histograms (`scores` present, no
      `overall_score` → filled).
- [ ] Unit tests green: empty scores → None (not 0) + mean cases.
- [ ] Summary returns **numeric** `overall_score` for scored videos.
- [ ] Harness discovery passes on numeric-score filter.

## Dependencies

- **Blocked By**: —.
- **Blocks**: —.

## Estimated Effort

- [S/M] (formula + worker write + backfill + tests)
