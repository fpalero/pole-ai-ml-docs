# Ticket: PAIML-POLE-API-073

## Title
[Pipeline] Classify before phase detection — single detection pass with the correct reference histograms

## Description
Phase 25 (PLAN_PHASE_25.md, PO directive). Reorder `AnalyzeWorker.run_video_pipeline`: today
detection (stage 3) runs before classification (stage 4) and a corrective second detection pass
exists for the auto-label case. New order: **Extraction → Processing → Classification → Phase
detection → Summary**, where detection runs exactly ONCE using the effective label (explicit >
classified > fallback), guaranteeing the comparison uses the correct class's
`skeleton_trick_histograms`.

## What to Do (Implementation Steps)
- [ ] Move classification before detection in `run_video_pipeline`; compute `effective_label`
      (explicit request label > classified label > '') BEFORE detection.
- [ ] Single `_detect_phase_frames` call with the effective label; delete the corrective re-run
      block; persist bounds/phases exactly once as today.
- [ ] Keep: manual `phase_frames` authority (request/video doc skip detection), error isolation of
      detection failure, insights pre-compute, summary analyzed flag, result dict shape.
- [ ] Update ANALYZE_STAGES order + docstrings; confirm FE ProgressPanel maps stages BY KEY (check
      app/pole_analyst progress panel component) — coordinate spec updates if any assert order.
- [ ] Tests: update worker tests to new order; add regression: auto-label case runs detection ONCE
      (mock call count) with the classified label's references; no-label+no-classification case
      keeps provisional bounds and skips detection gracefully.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Detection executes exactly once per analysis, always with the effective (classified) label.
- [ ] All worker/endpoint tests green (`pixi run test-api`); coverage maintained.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api`

## Dependencies
- Blocks: none · Blocked By: none · Effort: [M]
