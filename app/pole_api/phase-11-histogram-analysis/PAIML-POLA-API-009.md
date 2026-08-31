# Ticket: PAIML-POLA-API-009

## Title
[Application] Refactor `ToolsService` (add histogram methods; remove reference/attempt/threshold/analyze)

## Description
Phase 11 (§8.3.2 bullet 3). Extend `ToolsService` with `submit_histogram_analysis`, `get_histogram`,
`patch_histogram_phases`, and remove the legacy reference/attempt/threshold/analyze methods and their
repository constructor params (including the `threshold_discovery` import).

## What to Do (Implementation Steps)
- [ ] Step 1: Add `submit_histogram_analysis`, `get_histogram`, `patch_histogram_phases` delegating to `HistogramAnalysisService` / `HistogramRepository`.
- [ ] Step 2: Remove `save_reference_metrics`, `get_reference_metrics`, `save_reference_thresholds`, `get_reference_thresholds`, `discover_thresholds`, `get_thresholds`, `analyze`, `get_attempt`, `_load_reference`, `_validate_phase_frames`, `_phase_durations`.
- [ ] Step 3: Remove the reference/attempt repository constructor params and the `threshold_discovery` import.
- [ ] Step 4: Keep `crop/shift/correct/histogram/similarity` intact.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `ToolsService` exposes only the retained + new methods; no reference/attempt/threshold/analyze surface remains.
- [ ] No `threshold_discovery` import remains; lints clean.
- [ ] `histogram`/`similarity` still call `pole_tools` directly (unchanged).

## Integration Tests to Run (Local Verification)
- [ ] UC-91/92/93 (new methods), plus regression on crop/shift/correct.

## Dependencies
- **Blocks**: PAIML-POLA-API-013, PAIML-POLA-API-015, PAIML-POLA-API-017
- **Blocked By**: PAIML-POLA-API-007, PAIML-POLA-API-008

## Estimated Effort
- [M]
