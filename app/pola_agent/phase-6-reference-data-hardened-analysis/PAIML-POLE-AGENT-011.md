# Ticket: PAIML-POLE-AGENT-011

> **Status: IMPLEMENTED (library) / API wiring DEFERRED (2026-08-13).** `PhaseDetector` exists in
> `pole_tools/phase_detector.py` (PD-01..05) and is used by `pole_tools.histogram_analyzer`
> (`detect_phase_boundaries`), with a <100 ms perf test in the hardening suite. **Deferred:**
> wiring `PhaseDetector` into `pola_api /histograms/analysis` as a fallback when `phase_frames` are
> missing (the endpoint still skips clips without manual `phase_frames`).

## Title
[Application] Automatic phase detection (PD-01..05) — replace manual `phase_frames`

## Description
Phase boundaries are currently provided manually (`phase_frames`) by the user or
caller.  This ticket implements the automatic phase-detection state machine
(PD-01..05 from `agent_requirements.md` §4) so `HistogramAnalyzer` can derive
ENTRANCE / EXECUTION / EXIT boundaries from the metric signals alone.

State machine:
- **PD-01** — Initialize state as `ENTRANCE` at frame 0.
- **PD-02** — Transition `ENTRANCE -> EXECUTION` only when ALL of: wrist
  stability below threshold, horizontal speed below brake, and angular speed
  above `angular_acceleration_spike * 0.5` (AND logic, no isolated false
  positives).
- **PD-03** — Transition `EXECUTION -> EXIT` when vertical speed crosses below
  `vertical_speed_cross_zero - 0.05` after being positive for the prior 3
  frames.
- **PD-04** — Debounce: ignore conditions for `0.1 * fps` frames after a state
  change.
- **PD-05** — Fallback: if no transition by 50% of the video, force boundaries
  using `fallback_percentages` from the `reference_thresholds` config.

Thresholds come from `reference_thresholds` (produced by
PAIML-POLE-AGENT-010); fall back to conservative defaults only if the config is
absent and the DB is unseeded.  Output must keep `end_of_entrance_frame` /
`end_of_execution_frame` as absolute indices and the phase-range dict
(`{"ENTRANCE": [0, e1], "EXECUTION": [e1, e2], "EXIT": [e2, n]}` — PD-06/PD-07).
Automatic detection is only engaged when `phase_frames` is not provided.

## What to Do (Implementation Steps)
- [ ] Implement a `PhaseDetector` (in `pole-tools`, e.g.
  `src/pole_tools/phase_detector.py`) exposing
  `detect(metrics, fps, thresholds) -> PhaseBoundaries`.
- [ ] Implement the state machine per PD-01..PD-04 (init, AND-condition
  transitions, vertical-speed crossing, debounce window).
- [ ] Implement the PD-05 fallback using `fallback_percentages` when no
  transition fires by 50% of frames.
- [ ] Wire `ThresholdConfig` loading into `PhaseDetector` (inject a
  `get_thresholds` callable; the 422/not-trained case is handled by the caller).
- [ ] Integrate into `HistogramAnalyzer`: when `phase_frames` is `None`, call
  `PhaseDetector` with the computed M-01..M-04 signals and the trick type's
  thresholds.
- [ ] Return `end_of_entrance_frame`, `end_of_execution_frame`, and the
  phase-range dict in the analysis result (backward compatible: keep existing
  fields, add new ones).
- [ ] Unit tests: each transition rule, debounce, fallback, boundary output
  (PD-06/PD-07), and `phase_frames`-provided path unchanged.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `PhaseDetector` returns absolute boundaries matching manual labels within
  ±3 frames on ≥ 10 labeled videos (accuracy gate from §9.2).
- [ ] All PD-01..PD-05 rules are covered by unit tests.
- [ ] `HistogramAnalyzer` uses automatic detection when `phase_frames` is not
  provided and still honors explicit `phase_frames` when given.
- [ ] No regressions in `pixi run test` / `pixi run test-chatbot` /
  `pixi run test-api`.
- [ ] ≥ 80% coverage on the new phase-detection code.

## Integration Tests to Run (Local Verification)
- [ ] HA-H1: clean STATIC trick — phases within ±2 frames of manual label.
- [ ] HA-H2: known execution flaw — critical frame still lands in EXECUTION
  with Z > 2.0.
- [ ] HA-H4: MOMENTUM trick — vertical hip peak triggers the transition.
- [ ] Measure phase detection latency on a 150-frame video (< 100 ms target).

## Dependencies
- **Blocks**: PAIML-POLE-AGENT-012
- **Blocked By**: PAIML-POLE-AGENT-010 (thresholds config), PAIML-POLE-AGENT-009
  (seeded reference data for Z-score/validation)

## Estimated Effort
- [L]
