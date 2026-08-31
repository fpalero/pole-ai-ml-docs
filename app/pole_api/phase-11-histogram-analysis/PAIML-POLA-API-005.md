# Ticket: PAIML-POLA-API-005

## Title
[Infrastructure] Mirror the 8 metric names in `pole_tools/histogram_analyzer.py` and single-source `METRICS`

## Description
Phase 11 (§8.3.1). `pole_tools/histogram_analyzer.py` (`METRIC_NAMES` + `compute_metrics`) still uses
the legacy set. Mirror the authoritative 8 and ensure `pole_tools/services/histogram.py` `METRICS` (the
M-01..M-08 dict) is the single source consumed by both the analyzer and the processor.

## What to Do (Implementation Steps)
- [ ] Step 1: Update `pole_tools/histogram_analyzer.py` `METRIC_NAMES` to the authoritative 8 (drop angles, rename `body_tilt_angle`→`body_tilt`).
- [ ] Step 2: Update its `compute_metrics` to emit the same 8 keys (align with the processor).
- [ ] Step 3: Confirm `pole_tools/services/histogram.py` `METRICS` remains the single M-code→name map; remove any duplicate/stale name list.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `histogram_analyzer.py` and `histogram_processor.py` emit identical 8 metric keys.
- [ ] `METRICS` in `services/histogram.py` is the canonical source; no stale name lists remain.
- [ ] Imports/lints clean; no behavior change beyond names.

## Integration Tests to Run (Local Verification)
- [ ] UC-91 / UC-94 (after downstream) — analyzer/processor names stay consistent.

## Dependencies
- **Blocks**: PAIML-POLA-API-006
- **Blocked By**: PAIML-POLA-API-002

## Estimated Effort
- [S]
