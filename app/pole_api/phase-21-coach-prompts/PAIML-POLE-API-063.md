# Ticket: PAIML-POLE-API-063

## Title
[Application] Coach services — deterministic data gather + one-shot LLM call + persistence

## Description
Phase 21 (§2, PLAN_PHASE_21.md Phase B). Implement `analysis/services/coach_service.py`: one
service that gathers the prompt inputs deterministically from the existing analysis repositories,
fills the registry templates (PAIML-POLE-API-062), makes a **single** `OllamaLLM` call per action,
validates the JSON reply, and persists the envelope on the video doc. No ReAct loop, no tools.

Persistence on `analysis-db.videos`:
- `coach_summary` = `{content, model, generated_at}`
- `coach_plan` = `{target_trick, content, model, generated_at}`
- `coach_pose` = `{frame, content, model, generated_at}`

Regeneration is last-write-wins. LLM-down and invalid-JSON degrade to structured error payloads —
the WS/HTTP layer never crashes.

## What to Do (Implementation Steps)
- [ ] `CoachService` with injectable deps: `video_repo`, `histogram_repo`, `landmark_repo`, `llm`,
      `settings` (mirrors `AnalyzeWorker` injectable style; hermetic unit tests without Mongo/Ollama).
- [ ] Input gathering: summary fields (`z_mean`, `scores`, `detections`, `critical_*`) via
      `AnalysisHistogramRepository`; landmark-derived per-phase metric deviations +
      `resampled` signal stats; pose issues reuse of `analysis.services.pose_service.build_pose_issues`.
- [ ] One LLM call per action using the shared `OllamaLLM` config (`settings.ollama_model/host`);
      accept an injected client (wiring reuses/exposes the existing instance pattern from
      `main._build_analyst_chatbot_deps`).
- [ ] JSON parse + schema validation with exactly 1 retry on failure; structured degradation payload
      after the retry (`{"error": "llm_invalid_json" | "llm_unavailable", ...}`).
- [ ] Persist envelopes via `AnalysisVideoRepository.update`; idempotent regeneration.
- [ ] Decide + implement numeric grounding post-check (advisory flag vs hard reject) — see Open
      Question in PLAN_PHASE_21.
- [ ] Unit tests: happy path, invalid JSON → retry → degradation, LLM exception → degradation,
      not-analyzed video guard, persistence shape, regeneration overwrite.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] All three coach actions work end-to-end against a fake LLM + mongomock repos.
- [ ] No image bytes are read or passed anywhere in the pose flow.
- [ ] Degradation payloads are structured and typed.
- [ ] Coverage ≥ 80% for the new module.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs)

## Dependencies
- **Blocks**: PAIML-POLE-API-064
- **Blocked By**: PAIML-POLE-API-062

## Estimated Effort
- [M]
