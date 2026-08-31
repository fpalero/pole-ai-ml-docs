# Ticket: PAIML-POLE-AGENT-014

## Status
✅ DONE — Implemented

## Title
[Application] Training chatbot (Path A) — `training_chatbot` slice in `pola_api`

## Description
Phase 7 adds a conversational assistant for the ML training workflow.  Per
`implementation_plan.md` §13.5, start with **Path A**: a thin ReAct agent slice
in `pola_api` (`app/pola_api/src/training_chatbot/`) that coaches data
scientists through training tasks:

- Hyperparameter search (epochs, learning rate, window size).
- Model comparison (LSTM variants / training runs).
- Dataset statistics and quality checks.
- Job inspection (training job status via `pole-jobs`).

Unlike the video-analysis chatbot, the training chatbot talks directly to
`pole_ml` and `pole-jobs` (single process, no proxy).  If traffic/tool set
grows, Path B extracts it to `packages/training-chatbot` behind the same FE WS
contract (`WS /ws/training-chat`).  Record the Path A→B extraction path in
`implementation_plan.md` §13.5 when this ships.

## What to Do (Implementation Steps)
- [x] Create `app/pola_api/src/training_chatbot/` slice (`__init__`,
  `router.py`, `deps.py`) with `WS /ws/training-chat`.
- [x] Define the training-tool registry: hyperparameter search, model
  comparison, dataset stats, job inspection (wrapping `pole_ml` training APIs
  and `pole-jobs` `JobOrchestrator`).
- [x] Reuse the ReAct agent core (from `packages/chatbot`) with a
  training-specific system prompt and tool registry.
- [x] Wire session state reuse (Phase 5 `ChatbotSession` or a training variant)
  with `session_id` resume.
- [x] Add job event relay for training jobs (`job_started`/`progress`/`done`/
  `error`) over `WS /ws/training-chat` (reuse `JobEventPublisher` + subscriber).
- [x] Enforce the chatbot→tools import rule equivalent here: the training
  chatbot imports `pole_ml`/`pole-jobs` only through a thin service facade.
- [x] Add LLM availability handling: `opencode serve` down → fallback advice or
  503 (mirror UC-AG-05 behavior).
- [x] Unit tests: tool registry invocation, agent loop, session resume, job
  relay; ≥ 80% coverage on the slice.
- [x] Document the Path A → Path B extraction trigger and contract in
  `implementation_plan.md` §13.5.

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] `WS /ws/training-chat` accepts connections and answers training-domain
  questions using the ReAct loop.
- [x] Training tools (hyperparam search, model compare, dataset stats, job
  inspection) are invocable and return structured results.
- [x] Training job progress is relayed to the WS client.
- [x] Sessions resume via `session_id`.
- [x] LLM-down path returns fallback advice / 503 without crashing.
- [x] Unit tests green, ≥ 80% coverage; no regressions in `pixi run test-api`.
- [x] FE WebSocket contract documented so PAIML-POLE-AGENT-013 (or a future
  training FE) can connect.

## Integration Tests to Run (Local Verification)
- [x] Connect to `WS /ws/training-chat`, ask a dataset-stats question — verify
  structured reply.
- [x] Trigger a training-job inspection — verify job events relayed.
- [x] `pixi run test-api` — full suite green.

## Dependencies
- **Blocks**: None (final phase)
- **Blocked By**: Phase 5 chatbot infrastructure in `pola_api`
  (PAIML-POLE-AGENT-008) is a soft prerequisite (ReAct core + session service
  reuse).

## Estimated Effort
- [L]
