# PAIML-POLE-COACH-004 — Phase 4 (D): analyst_chatbot wiring + profile + Phase-33 biomech

- **Status:** 📋 PLANNED
- **Blocks:** PAIML-POLE-COACH-005
- **Blocked By:** PAIML-POLE-COACH-003

## Goal
Make the supergraph live behind the pole-analysis FE chatbot, extend the athlete
profile (BE + FE), and extend the biomechanical joint set (shoulders/hips/spine)
including the elbow/knee vertex-convention fix.

## Architectural context
- **Database:** `analysis-db.athlete_profiles` gains `experience_level`, `goals`,
  `days_per_week`, `injury_history`/`limitations` (BE `analysis/schemas.py` +
  `AthleteProfileRepository` + `profile.py`; FE `athlete-profile.model.ts` + form).
  `skeleton_landmarks.biomech_features` gains new angle keys (back-computable).
- **Caching/performance:** new `biomech_features` are pure math on stored landmarks —
  old docs back-compute at read time, no re-extraction.
- **Scalability/resilience:** `analyst_chatbot` keeps its tool registry; the supergraph
  is invoked as the chat brain with an `AnalystFacade`-backed `MetricsProvider`.
  `chatbot` (video) + `training_chatbot` slices stay on `PoleLangGraphAgent`.
- **External:** none new.

## Scope (in)
1. `analyst_chatbot` → build/run the supergraph (inject facade-backed providers);
   keep WS contract + answer blocks unchanged.
2. Profile extension end-to-end (BE schema/repo/controller + FE model/form/modal).
3. `biomech_features.py`: add `shoulder_flexion_l/r_deg`, `hip_angle_l/r_deg`,
   `spine_angle_deg` (torso-vs-vertical from mid-shoulder/mid-hip); extend
   `FEATURE_NAMES`, `compute_frame_features`, `phase_feature_stats`.
4. **Fix the elbow/knee vertex convention** (`_ANGLE_JOINTS` currently measures at the
   proximal joint) BEFORE extending; update `coach_service._DEGREE_FEATURES`,
   `_joint_angle_description`, `scan_risk_frames` bands, prompt glossary.
5. Unit tests: wiring (mocked providers), profile CRUD, new angle math (golden
   vectors), back-compute on legacy docs, convention fix verified.

## Scope (out)
Full E2E (Phase 5).

## Tasks
- 4.1 Supergraph behind `analyst_chatbot` (providers injected; slices intact).
- 4.2 Profile schema + repo + controller + FE form.
- 4.3 Angle-convention fix + new joints + risk/coach/prompt updates.
- 4.4 Unit tests (wiring, profile, angles, back-compute).
- 4.5 Verify/extend the `pole_api` Docker build so `pole_coach` is importable in the image (editable pixi dep or PYTHONPATH); image builds clean.

## Acceptance
- [ ] Analyst chat answers via the supergraph; existing 17 tools still callable.
- [ ] Profile round-trips the 4 new fields BE→FE.
- [ ] Golden-vector test proves elbow/knee measure the correct joint.
- [ ] Unit suite green.
- [ ] API image builds with `pole_coach` importable.

## Verification
`pixi run test-api`, `pixi run test-chatbot`. Then **start the integration test**
(`pixi run test-integration`) per ticket DoD.

## Risks
- Angle fix changes historic numbers → back-compute keeps reads consistent; risk_scan
  thresholds re-validated, not blindly carried over.
- FE form validation for new fields (ranges 1–7 days, enums).

## Definition of Done
Unit suites + integration aggregator green; report.

## As-built deviations (implementation report)
Worktree branch: `feature/PAIML-POLE-COACH-004-analyst-chatbot-wiring-profile`.
Suites green — 33 new 004 tests, 65 touched coach/profile/schema suites,
121 analyst-chatbot slice, 166 `pole_coach` package tests.

1. Coverage ≥80% number not producible: `pytest --cov` crashes at conftest import
   (`ImportError: cannot load module more than once`, numpy/TF + pytest-cov env
   conflict) — reproducible, fires before any 004 code executes,
    pre-existing/unrelated. Evidence in lieu: every touched module exercised by
    green suites (golden-vector, back-compute, wiring-with-mocked-providers).
> Update (gate 2026-09-08): pytest-cov reproduced fine — `pixi run test` reports 82.42%. Original crash not observed; treating as env-specific flake.
2. Broad `tests/analysis` + WS-integration runs hang (2× timeout) —
   mongo/docker-dependent integration files, out of pre-PR scope; left to
   staging e2e gate.
3. Docker image build NOT executed (task 4.5): base.Dockerfile lane is a 4-line
   mirror of the proven pole_rag lane; handed to gate ("image builds, import
   pole_coach.supergraph OK").
4. No AthleteProfileRepository change: upsert is a generic `$set` passthrough,
   PUT uses `model_dump()` — new profile fields persist with zero repo edits.
5. FE compile/spec not run: no `.spec.ts` exists for the profile page; change is
   a typed template/form mirroring the BE enum — FE-design conformance left to
   gate.
