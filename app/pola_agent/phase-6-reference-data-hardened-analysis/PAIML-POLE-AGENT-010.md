# Ticket: PAIML-POLE-AGENT-010

> **Status: SUPERSEDED (2026-08-13).** The new histogram design uses a **fixed** `|z| > 1` detection
> threshold (no LLM-discovered, configurable thresholds). The `discover_thresholds.py` CLI and
> `pixi run discover-thresholds` task were **removed** (they targeted the deleted
> `/api/tools/reference/thresholds/discover` endpoint). Content below is historical.

## Title
[Application] LLM threshold discovery (LLM-TD-01..04) → `reference_thresholds`

## Description
Phase detection needs trick-specific thresholds (wrist stability, horizontal
speed brake, vertical speed cross-zero, angular acceleration spike, and
fallback percentages).  These are currently fixed/hard-coded; this ticket makes
the system derive them from the seeded `reference_metrics` data via the OpenCode
LLM (`opencode serve`).

Flow (LLM-TD-01..04 from `agent_requirements.md` §7.1):
1. Aggregate `reference_metrics` (mean/std/gradient per normalized index) for
   the 3 mandatory metrics (horizontal_speed, vertical_speed, angular_speed)
   into a compact JSON summary (~5-8 KB).
2. Send the summary to the LLM with the §7.3 prompt to suggest
   `end_of_entrance_frame`, `end_of_execution_frame`, and
   `suggested_numeric_thresholds`.
3. Validate the response: `0 < end_of_entrance_frame < end_of_execution_frame
   < 100` (LLM-TD-03).  On invalid JSON or bounds, re-prompt with a correction
   instruction (bounded retries, e.g. 2).
4. Persist the validated config to the `reference_thresholds` PostgreSQL table
   via the Phase 4 repo/endpoint, keyed by `trick_type` (LLM-TD-04).

This is a one-time-per-trick-type cost (< 30 s).  It is what powers automatic
phase detection (PAIML-POLE-AGENT-011) and is validated end-to-end by HA-H5.

## What to Do (Implementation Steps)
- [ ] Add a threshold-discovery service under the `tools` slice (or `pole-tools`
  if LLM-agnostic): `discover_thresholds(trick_type) -> ThresholdConfig`.
- [ ] Implement the aggregation step: read `reference_metrics` rows for the
  trick type, resample to 100 normalized points, and render a compact JSON
  summary (frame, mean, std, gradient per metric).
- [ ] Reuse `OpenCodeLLMClient` to send the §7.3 prompt with the summary
  payload.
- [ ] Implement response validation (LLM-TD-03): JSON parse, bounds check
  `0 < entrance < execution < 100`, threshold fields present.
- [ ] Implement bounded re-prompt loop (max 2 retries) with a stricter JSON-only
  instruction on failure; on final failure raise `LLMError` → surfaced as 503.
- [ ] Persist the validated `ThresholdConfig` into `reference_thresholds` via the
  existing repository/endpoint (`POST /api/tools/reference/thresholds`).
- [ ] Add a lookup path: `get_thresholds(trick_type)` that raises a clear
  "not trained" 422 when no config exists (feeds PAIML-POLE-AGENT-011).
- [ ] Unit tests: aggregation format, validation happy path, invalid-bounds
  re-prompt, persistence (in-memory repo), 422 on missing config.
- [ ] Provide a pixi task / CLI (`pixi run discover-thresholds --trick STATIC`)
  so the bootstrap can be run per trick type.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `discover_thresholds` returns a validated config with bounds
  `0 < entrance < execution < 100` and all four suggested thresholds.
- [ ] Validated config is stored in `reference_thresholds` (verify via
  `GET /api/tools/reference/thresholds`).
- [ ] Invalid LLM JSON/out-of-bounds triggers a re-prompt; after max retries the
  call fails with a 503-compatible error.
- [ ] Missing config raises a 422 "Reference thresholds not trained" (HA-S5).
- [ ] Unit tests pass; no regressions in `pixi run test` / `pixi run test-api`.
- [ ] ≥ 80% coverage on the new discovery code.

## Integration Tests to Run (Local Verification)
- [ ] Run UC-AG-01..06 regression — threshold discovery must not break the
  existing in-memory analysis path (HistogramAnalyzer still works unseeded).
- [ ] HA-H5: run `pixi run discover-thresholds --trick STATIC` against seeded
  DB — verify valid JSON stored with correct bounds.
- [ ] `pixi run test-api` — tools endpoints green.

## Dependencies
- **Blocks**: PAIML-POLE-AGENT-011, PAIML-POLE-AGENT-012
- **Blocked By**: PAIML-POLE-AGENT-009 (needs seeded `reference_metrics`)

## Estimated Effort
- [L]
