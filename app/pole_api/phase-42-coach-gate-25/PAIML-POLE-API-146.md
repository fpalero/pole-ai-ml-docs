# Ticket: PAIML-POLE-API-146

## Title
[Tests] Investigate + fix model/LLM-dependent `test-api` failures (real-predictor + coach-flow)

## Description
`pixi run test-api` is RED on the tests that exercise the **real ML/LLM path**. Two clusters
(reproduced 2026-09-25, deterministic — not collision, not flake):

1. **`tests/analysis/test_analyze_worker.py` — real-predictor classification (3 FAILED):**
   - `test_worker_classification_real_predictor_runs_before_detection`
   - `test_worker_classification_real_predictor_with_desconocido_detection`
   - `test_worker_integration_autolabel_single_detection_pass`
   These instantiate the real `HybridClassifierPredictor` (LSTM + ChromaDB). Suspected cause:
   missing model artifact (`.keras`) / unseeded ChromaDB in the local env.

2. **`tests/analysis/test_coach_flow_integration.py::TestCoachFlowPipeline` — fixture ERROR
   (~7 ERRORs):** `test_worker_persists_insights_during_analysis`, `test_get_coach_insights_serves_computed_data`,
   `test_summary_scores_against_seeded_cohort`, `test_coach_summary_generate_then_cached`,
   `test_coach_plan_with_target_trick`, `test_pose_analysis_text_only`, `test_llm_down_503_but_insights_still_served`.
   A targeted run of the first test hangs (no output within 5 min) — consistent with a
   setup fixture blocking on a real LLM call or model load.

Determine the exact cause and make these tests deterministic in CI/local without external
side effects (mock the LLM, fake the predictor, or mark them `integration`/skip when the
artifact is absent — never hard-depend on a live model or live LLM in the unit gate).

## Repository
pole-ai-ml

## Affected
- `app/pole_api/tests/analysis/test_analyze_worker.py`
- `app/pole_api/tests/analysis/test_coach_flow_integration.py`
- (if needed) the corresponding fixtures in `app/pole_api/tests/conftest.py`

## What to Do (Implementation Steps)
- [ ] Step 1: Reproduce each failure with `--tb=short` and record the exact exception (artifact path? import? LLM timeout?)
- [ ] Step 2: For the real-predictor tests — either provide/seed the model + ChromaDB fixture, or swap in a fake predictor for the classification-order assertions (the ordering is what's under test, not model accuracy)
- [ ] Step 3: For the coach-flow tests — replace the blocking LLM dependency with a mock/recording, or gate the real-LLM cases behind `-m integration`
- [ ] Step 4: Ensure `test-api` (or at least these two files) is GREEN and fast (no 5-min hangs)

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] The two failing files pass deterministically with no live model/LLM hard dependency
- [ ] `pytest tests/analysis/test_analyze_worker.py tests/analysis/test_coach_flow_integration.py` GREEN in <5 min
- [ ] No test hangs on a network/model call; any real-LLM case is `-m integration`-gated

## Dependencies
- **Blocks:** None
- **Blocked By:** None
- **Related:** PAIML-POLE-API-073 (classify-before-detect)