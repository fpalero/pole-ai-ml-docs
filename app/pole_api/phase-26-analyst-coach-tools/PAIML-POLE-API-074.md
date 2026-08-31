# Ticket: PAIML-POLE-API-074

## Title
[Application] Analyst chatbot tool `compare_sessions` — session-over-session metric comparison

## Description
Phase 26 (PLAN_PHASE_26.md), tool #1. Adds a sync `compare_sessions` chatbot tool so the coach can
ask "did I improve vs last session?" over the analyst WS. Thin adapter over the Phase 24
`MetricDeltasService.compute(video_id)` (already resolves the latest prior analyzed video of the
same trick and returns per-metric `delta_pct` + `improved` + `peak_flags`). No new analysis math.

## What to Do (Implementation Steps)
- [ ] `AnalystFacade.compare_sessions(video_id, baseline_video_id=None)` — call
      `MetricDeltasService.compute(video_id)`; optional explicit `baseline_video_id` forces the
      baseline (compare against a specific prior video instead of the auto-resolved one). Wrap the
      service's `NotFoundError`/`ConflictError` into structured `{"error": ...}` dicts (never raise
      to the WS); empty `metrics` with a `None` baseline returns clean data the agent relays as
      "no comparable session yet".
- [ ] Return payload (compact, agent-facing): `{video_id, baseline_video_id, metrics: [{key,
      current, previous, delta_pct, improved}], peak_flags: [{key}], hint_to_agent}` — hint
      instructs the agent to present improved/regressed metrics as a markdown table and flag peaks.
- [ ] Register `ToolSpec(name="compare_sessions", mode="sync", ...)` in
      `analyst_chatbot/tools.py` (`ANALYST_TOOL_NAMES` + `register_analyst_tools`), params
      `{video_id: string (required), baseline_video_id: string}`.
- [ ] Add one line to `ANALYST_SYSTEM_PROMPT` tool list + keep the "N tools are the ONLY tools"
      sentence accurate.
- [ ] Tests: facade unit tests (improved/regressed deltas, empty-baseline, explicit baseline,
      not-analyzed error) + tool-registry registration test.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Tool returns per-metric deltas vs the auto-resolved (or explicit) baseline; missing keys and
      zero-baseline keys omitted — never fabricated.
- [ ] Never raises to the WS; `{"error": ...}` relayed for unknown video / not-analyzed video.
- [ ] `pixi run test-api` green; coverage ≥ 80% maintained.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs)

## Dependencies
- **Blocks**: PAIML-POLE-API-079 (`progress_trend` reuses the same baseline resolution)
- **Blocked By**: Phase 24 (`MetricDeltasService`, PAIML-POLE-API-072, merged)

## Estimated Effort
- [S]
