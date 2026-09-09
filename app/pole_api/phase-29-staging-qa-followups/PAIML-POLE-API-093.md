# Ticket: PAIML-POLE-API-093

## Title
[Chatbot] Staging QA follow-ups: image-serving endpoint + path-leak strip + `segment_insight` trim + distinct failed-turn signal

## Description
Phase 29 — see [PLAN_PHASE_29](../plan/PLAN_PHASE_29.md). Follow-up bundle from the
phase-23 staging QA gate (40-question battery through the real FE at staging).

Root causes established by the staging gate. Tester evidence (local, not committed):
`/tmp/opencode/staging-battery/` (`summary.json`, `ws-triage.json`, `run.log`, `shots/`,
`cards/`) and `/tmp/opencode/tool08-repro/` (`tool08-frames.json`, `repro.mjs`, `diag.mjs`):

- (a) **Image-serving endpoint.** Analysis artifacts (frames, histograms under
  `/data/uploads/…`) are referenced by container-local paths the browser cannot load.
  TOOL-04/TOOL-18-class turns render `md` only (`missing cards: image` in `summary.json`)
  because the `image` block `src` is not a reachable URL.
- (b) **Path-leak strip.** Absolute server paths must never appear in user-visible prose
  (same fix family as (a); TOOL-04 rendered `/data/uploads/…` bullets in the `md` reply).
- (c) **Trim `segment_insight`.** Its tool payload inflates the follow-up LLM call to ~112k
  tokens, which caused an OpenRouter 402 → ABANDONED turn: the TOOL-08-class question
  ("What happened during the execution phase (seconds 2-6) of my handspring video?",
  see `tool08-frames.json` — `agent_reply` with generic fallback
  "I'm having trouble understanding…", `tool_calls: []`) never produces its card and the
  turn is indistinguishable from a normal completion.
- (d) **Distinct failed-turn signal.** ABANDONED/error turns currently surface as
  chip `Completed` + generic fallback `md` (see `tool08-frames.json`: `"chipFinal": "Completed"`,
  fallback text). They must emit an explicit, machine-readable error status instead, so
  `pole_analyst` Phase 24 (`PAIML-POLE-ANALYST-073`) can render a failed turn distinctly.

## What to Do (Implementation Steps)
- [ ] (a) Add an authenticated HTTP GET endpoint serving analysis artifacts (frames,
      histograms) by stable id/path (never expose raw filesystem layout); set correct
      `Content-Type` (+ `Content-Length`/`Cache-Control` as appropriate); return `404` for
      unknown ids and `401/403` without valid auth. Make `image` blocks carry the reachable
      endpoint URL in `src` — never a container-local path. Keep the existing block shape
      (`analyst_chatbot/blocks.py`) so the FE `image` renderer needs no contract change
      (verify-only on the FE side, cf. `PAIML-POLE-ANALYST-073`).
- [ ] (b) Strip absolute server paths from all user-visible chatbot prose: post-process
      `reply`/`md` synthesis (`blocks_to_text` / md synthesis path, cf. `PAIML-POLE-API-087`)
      to drop or rewrite `/data/…` (and any other absolute-path) segments; cover tool-error
      branches (`extract_frames`, `crop`, coach tools) that currently echo storage paths.
      Add a regression assertion helper (no `/data/` substring in any wire `reply`/`blocks[].content`).
- [ ] (c) Shrink the `segment_insight` tool payload returned to the follow-up LLM call:
      return only the execution-window slice the question asked for (truncate/summarize frames
      and per-frame detail, cap array lengths), and cap the follow-up completion `max_tokens`
      so a TOOL-08-class turn fits the model context/token budget. Document the chosen caps
      (payload items, chars, `max_tokens`) in code + tests.
- [ ] (d) Emit an explicit failed-turn signal for ABANDONED/error turns: a machine-readable
      error status on the `agent_reply` frame (e.g. `status: "error"` / error code — never
      bare `Completed`), plus a non-generic error `reply`/`md` and (where applicable) the
      failing `tool_calls` entry with its error. Keep the WS protocol backward compatible;
      document the frame shape for the FE consumer (`PAIML-POLE-ANALYST-073`).
- [ ] Add/update tests in `app/pole_api/tests/test_analyst_chatbot*.py` covering (a)–(d).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] (a) The new endpoint serves artifact bytes over HTTP with auth (200 + image bytes for a
      known artifact; 404 unknown; 401/403 unauthenticated); `image` block `src` values are
      HTTP(S) URLs, never container-local paths.
- [ ] (b) No `/data/` (or other absolute server-path) strings in any chatbot `reply`/`blocks`
      across the 40-question staging battery rerun (`RAG-01..20` + `TOOL-01..20`).
- [ ] (c) TOOL-08-class turns (`segment_insight` execution-window questions) fit the token
      budget: no OpenRouter 402 / context-overflow ABANDONED caused by the tool payload; the
      turn completes with its card instead of the generic fallback.
- [ ] (d) ABANDONED/error turns surface a machine-readable error status (not `Completed` +
      generic fallback); the FE can branch on it (consumer: `PAIML-POLE-ANALYST-073`).
- [ ] `pixi run test-api` green (guarded `_testing` DBs), coverage ≥ 80%.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs)
- [ ] Staging battery rerun: 40 questions through the real FE (`RAG-01..20`, `TOOL-01..20`);
      assert (b) no `/data/` strings, (c) TOOL-08-class turn completes, (d) forced-error turn
      carries the error status.

## Dependencies
- **Blocks**: `PAIML-POLE-ANALYST-073` (FE failed-turn error state consumes the (d) signal;
  FE `image` URL adoption consumes (a)).
- **Blocked By**: None (backend-only; evidence paths above are local tester artifacts).

## Estimated Effort
- [L]
