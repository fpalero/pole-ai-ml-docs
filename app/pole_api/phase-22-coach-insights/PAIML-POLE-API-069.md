# Ticket: PAIML-POLE-API-069

## Title
[Pipeline] Integrate coach insights into analysis worker

## Description
Phase 22 (§5). After `_score_video` in `AnalyzeWorker`, call `CoachInsightsService.ensure()`
to pre-compute insights during analysis. This ensures insights are ready when the FE or chatbot
requests them (Q5C: compute during analysis as default).

## What to Do (Implementation Steps)
- [ ] In `AnalyzeWorker._run()`, after `_score_video()` completes, call
  `CoachInsightsService.ensure(video_id)`.
- [ ] Catch and log any exceptions from insights computation — do not fail the analysis job
  if insights computation fails.
- [ ] Add timing: log how long insights computation takes.
- [ ] Unit tests: verify `ensure()` called after scoring, verify exception handling.
- [ ] Integration test: run analysis → verify `coach_insights` collection has data.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Analysis worker pre-computes coach insights after scoring.
- [ ] Insights computation failure does not fail the analysis job.
- [ ] Timing logged for insights computation.
- [ ] Unit tests pass for pipeline integration.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs; never prod).

## Dependencies
- **Blocks**: PAIML-POLE-API-071 (auto-suggestion needs deviation count)
- **Blocked By**: PAIML-POLE-API-067 (worker calls `CoachInsightsService.ensure()` directly;
  does not depend on the REST/chatbot layer -068)

## Estimated Effort
- [S]
