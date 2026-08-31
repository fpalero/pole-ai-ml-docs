# Ticket: PAIML-POLE-AGENT-009

> **Status: SUPERSEDED (2026-08-13).** Reference data no longer uses PostgreSQL. It is now the Mongo
> `skeleton_data.signal_histograms` cohort (mean/std per `(trick_label, metric)`, 300-pt), computed
> automatically by `pole_ml.HistogramDataProcessor` + `pola_api /histograms/analysis`. The
> `seed_reference.py` CLI and `pixi run seed-reference` task were **removed**. Content below is
> historical (Postgres-era plan).

## Title
[Infrastructure] Seed `reference_metrics` via ReferenceBuilder over labeled attempts

## Description
The `HistogramAnalyzer` currently uses a hard-coded in-memory dict for reference
statistics (mean/std per phase/metric).  Phase 6 moves this data into PostgreSQL
(`reference_metrics` table, already migrated in Phase 4) by running
`ReferenceBuilder` over the 21 labeled reference attempts.

This ticket covers the **seeding/bootstrap** path: writing the script/CLI that
reads labeled attempts, feeds them through `ReferenceBuilder.build()`, and
persists the aggregated statistics into the database repository created in
Phase 4.  Once seeded, `HistogramAnalyzer` can query the DB instead of the
in-memory fallback.

The seed must be idempotent (re-running overwrites existing rows for the same
trick+metric+phase combination) and must support a dry-run mode for validation.

## What to Do (Implementation Steps)
- [ ] Create a bootstrap/seed module under `packages/pole-tools/` (e.g.
  `src/pole_tools/seed_reference.py`) or a new pixi task that calls
  `ReferenceBuilder` with a list of labeled attempt paths.
- [ ] Define the input format: a JSON manifest listing labeled attempts with
  `video_path`, `trick_type`, and `phase_frames` (manual boundaries).
- [ ] Iterate over each labeled attempt: extract landmarks → compute metrics →
  call `ReferenceBuilder.process_attempt()` (or similar) to accumulate per-phase
  per-metric arrays.
- [ ] After all attempts are processed, call `ReferenceBuilder.build()` to
  produce `mean_array` and `std_array` (length 100 each) per
  trick_type/metric/phase.
- [ ] Persist the aggregated statistics into PostgreSQL via the
  `ReferenceMetricsRepository` (from Phase 4 `tools` slice) or via the `tools`
  API facade `POST /api/tools/reference/metrics`.
- [ ] Implement idempotency: on re-run, DELETE existing rows for the
  trick_type(s) being seeded and INSERT fresh, or use UPSERT with `ON CONFLICT`.
- [ ] Add a dry-run flag (`--dry-run`) that logs what would be inserted without
  touching the DB.
- [ ] Wire a pixi task (`pixi run seed-reference`) for one-command execution.
- [ ] Update `HistogramAnalyzer` to accept an optional `ReferenceMetricsRepository`
  and fall back to the in-memory dict only when the DB is empty (future ticket
  integration; just add the constructor parameter here).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Running `pixi run seed-reference --manifest data/labeled_attempts.json`
  populates `reference_metrics` with mean/std arrays for each trick type,
  metric, and phase.
- [ ] Re-running the seed is idempotent (same rows, no duplicates).
- [ ] Dry-run mode prints the expected rows without modifying the DB.
- [ ] Unit tests cover seed logic with an in-memory repository (fakeredis not
  needed; use the existing in-memory repo from Phase 4).
- [ ] No regressions in existing `pixi run test` (pole-tools) and
  `pixi run test-api` suites.

## Integration Tests to Run (Local Verification)
- [ ] Run `pixi run seed-reference` against a local PostgreSQL instance —
  verify rows appear in `reference_metrics`.
- [ ] Query `GET /api/tools/reference/metrics?trick_type=STATIC` and confirm
  the endpoint returns the seeded data.
- [ ] Run `pixi run test-api` — verify tools endpoints still pass.

## Dependencies
- **Blocks**: PAIML-POLE-AGENT-010, PAIML-POLE-AGENT-011
- **Blocked By**: None (Phase 4 repos + migration already in place)

## Estimated Effort
- [M]
