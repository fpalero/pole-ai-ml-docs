# Ticket: PAIML-POLE-API-127

## Title
gate-25 backend regression fix: terminal fallback flag + grounding lazy-fetch + metric_matrix contract

## Status
📋 PLANNED — follow-up fix for the 11 failing `pytest pole_api (scoped)` tests
(regressions from PR #322 / PAIML-POLE-API-122 supergraph FC1+FC2 work).

- **Status**: 📋 PLANNED
- **Project**: pole_api
- **Phase**: 42 coach-gate-25
- **Blocks**: none
- **Blocked By**: none — independent of 125/126; dependent only on the gate-25
  base already in develop.

## Context

11 backend tests fail on develop head. Proven **pre-existing** — the failures
reproduce on develop without the FE PR #323 (FE-only work does not touch these
BE paths); the regressions were introduced by the PR #322 / PAIML-POLE-API-122
supergraph FC1 + FC2 work. Three root causes:

### A — terminal fallback flag (8 tests)

`_terminal_fallback_turn` in the analyst supergraph emits `"fallback": False`
(regression from `True`). Affected tests:

- `failsafes_107` ×4 — `forced_failure_fallback_drives_terminal_frame`,
  `fallback_turn_never_runs_react_agent`,
  `terminal_fallback_synthesizes_text_when_conversion_drops`,
  `terminal_fallback_synthesizes_without_pole_coach_import`
- `grounding_115` ×2 — `unresolvable_fallback_stays_terminal`,
  `spent_budget_keeps_terminal_turn`
- `routing_residuals_116` — `unresolvable_turn_stays_terminal`
- `supergraph_wiring_004` — `supergraph_agent_emits_terminal_fallback`

All fail with `assert False is True` on the `fallback` field.

**Desired**: terminal fallback turns must set `"fallback": True` (keep `False`
only on success — this still lets the FE resolve the processing pill, since the
timeout frame already uses `fallback: True`).

### B — grounding lazy-fetch over-eager (2 tests)

1. `_DATA_ORIENTED_RE` matches bare technique words (e.g. "spin") → triggers an
   unnecessary latest-video / Mongo `find_one`
   (`grounding_115::test_no_video_reference_fires_no_extra_query` asserts the
   extra fetch returns `None`).
2. FC2 adds the latest-video leg even when `trick_name` already grounds the
   progress matrix
   (`routing_residuals_116::test_progress_with_trick_fetches_matrix` asserts
   `latest_calls == 0`).

**Desired**: once a trick is resolved (or for pure technique wording without
metric context), do NOT fire another latest-video lookup; keep the
single-snapshot guarantee.

### C — metric_matrix contract (1 test)

`make_fetch_trick_progress` (`pole_coach` `_common.py`, FC2) removed the
"metrics present → skip matrix fetch" short-circuit, so a grounded progress
turn (video with metrics) routes to
`AnalystTrickProgressProvider.get_trick_progress` →
`facade.get_progress_matrix(label)`, but the scenario `_FakeFacade` has no
`get_progress_matrix` → `AttributeError` → md-only output, no `metric_matrix`
block
(`scenarios_005::test_scenario_progress_reports_baseline_without_history`:
`assert 'metric_matrix' in {...}`).

**Desired**: either preserve the pre-122 LLM metric interpretation path when
metrics already exist, or reconcile the fake/contract with the deterministic
`progress_matrix` block type — the BE must consistently emit the matrix block
the FE renderer consumes.

## Acceptance Criteria

1. All 11 listed tests pass (`pytest` scoped as CI):
   ```bash
   pixi run test-api -- --ignore=tests/analysis --ignore=tests/test_e2e.py \
     --ignore=tests/test_analyst_ws_integration.py --ignore=tests/test_process.py \
     --ignore=tests/test_process_integration.py
   ```
2. Companion tests in the same 5 files (52 passing) still pass — no
   regressions.
3. Full `pytest pole_api (scoped)` CI job green.
4. FE renderer contract unchanged (the matrix block type the FE consumes stays
   consistent).

## Proposed Fix

Per root cause:

- **A** — supergraph `_terminal_fallback_turn` / `_build_state` (analyst
  supergraph, app/pole_api): emit `"fallback": True` on every terminal fallback
  frame; keep `False` only for success frames. Exact files located during
  implementation (test files: `failsafes_107`, `grounding_115`,
  `routing_residuals_116`, `supergraph_wiring_004`).
- **B** — `packages/pole_coach/src/pole_coach/_common.py`: tighten
  `_DATA_ORIENTED_RE` / `_is_data_oriented` so bare technique words do not
  trigger a latest-video lookup, and skip the FC2 latest-video leg when
  `trick_name` already grounds the progress turn (single-snapshot guarantee).
- **C** — `packages/pole_coach/src/pole_coach/_common.py`
  (`make_fetch_trick_progress`): restore the "metrics present → skip matrix
  fetch" short-circuit (pre-122 path), or reconcile the `_FakeFacade`
  contract with the deterministic `progress_matrix` block type so the BE
  consistently emits the matrix block.

## Verification

1. Reproduce locally on develop → 11 fail (the 5 test files: `failsafes_107`,
   `grounding_115`, `routing_residuals_116`, `supergraph_wiring_004`,
   `scenarios_005`).
2. Apply the fix.
3. Re-run the 5 test files → all 63 pass.
4. Full `pytest pole_api (scoped)` CI job green.

## Dependencies
- **Blocked By**: none (gate-25 base already in develop).
- **Blocks**: none (independent of 125/126).

## Estimated Effort
- [M]