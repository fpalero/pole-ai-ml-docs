# Ticket: PAIML-POLE-AGENT-015

## Title
[Refactor] Remove automatic phase detection (`PhaseDetector`) — phases are manual only

## Description
PO decision 2026-08-13: automatic phase detection is **no longer a requirement**. Phase boundaries
(`ENTRANCE` / `EXECUTION` / `EXIT`) are entered **manually** via
`PUT /api/training/clips/{video_id}/phase-frames` (there is no auto-detection API wiring, and none
will be added). Remove the `PhaseDetector` from `pole_tools` and the automatic fallback in
`histogram_analyzer` so any histogram/analysis path **requires** explicit `phase_frames` — no silent
auto-detection. Supersedes the deferred wiring item in `docs/app/pola_agent/PLAN.md` Phase 6 and the
future-work items in `docs/packages/pole_ml/PLAN.md` Phase 7 and `docs/packages/pole_tools/PLAN.md`
Phase 2.

## What to Do (Implementation Steps)
- [ ] Delete `packages/pole-tools/src/pole_tools/phase_detector.py`.
- [ ] `packages/pole-tools/src/pole_tools/histogram_analyzer.py`: remove the `PhaseDetector` fallback
      (auto-derive boundaries when `phase_frames` are absent, ~line 594–609). If `phase_frames` are
      missing, raise a clear error (or surface a documented skip reason) — do **not** auto-detect.
- [ ] Delete `packages/pole-tools/tests/test_phase_detector.py`.
- [ ] Update `packages/pole-tools/tests/test_hardening_analysis.py` and any other tests that reference
      `PhaseDetector` / phase-detection perf gates (<100ms PD test) to drop those references; keep the
      remaining hardening coverage.
- [ ] Update tests that relied on the auto-detection fallback to require explicit `phase_frames`.
- [ ] Docs: update `docs/packages/pole_tools/PLAN.md` (drop `phase_detector.py` from components,
      remove UC-TL-05 automatic phase detection, remove the "wire PhaseDetector fallback" Phase 2
      item), `docs/app/pola_agent/agent_requirements.md` (PD-01..05), and any other references to
      automatic detection. `docs/app/pola_agent/PLAN.md` Phase 6 + `docs/packages/pole_ml/PLAN.md`
      Phase 7 are updated by the team-lead separately (plan-level).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] No `PhaseDetector` / `phase_detector` references remain in `packages/` (code or tests).
- [ ] `histogram_analyzer` requires `phase_frames`; no automatic boundary derivation remains.
- [ ] `pixi run test-chatbot` and `pixi run test` (pole-train-model) green; `pixi run test-hardening`
      updated (or its removed tests dropped) and green; ≥80% coverage on `pole_tools`.
- [ ] Docs updated: automatic phase detection is documented as **removed**; phases are manual only.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test` (pole-train-model, includes `pole_tools` unit tests).
- [ ] `pixi run test-chatbot` (chatbot unit, excludes integration).
- [ ] `pixi run test-hardening` (updated suite).

## Dependencies
- **Blocks**: None.
- **Blocked By**: None (independent; runs in parallel with `PAIML-POLE-ML-001` and
  `PAIML-POLA-API-036..038`).

## Estimated Effort
- [M]
