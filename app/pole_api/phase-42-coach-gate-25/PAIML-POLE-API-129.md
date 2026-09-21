# Ticket: PAIML-POLE-API-129

## Title
Analyst ReAct sub-budget deadlock (Class B, gate blocker): raise `agent.run` `max_turn_seconds` below the WS guard (VA-05, VA-02)

## Status
📋 PLANNED — follow-up gate-fix ticket for phase-42 coach-gate-25, SAMPLE-5 gate
run `sample5-647d57e-20260921-205203` (**15/25, RED**).

> Summary: analyst ReAct sub-budget deadlock — `agent.run` `max_turn_seconds`
> (120 s) fires before the 300 s WS per-turn guard → terminal
> `error_code: turn_timeout` on long composed chains (VA-05/VA-02).

- **Status**: 📋 PLANNED
- **Project**: pole_api (backend lane)
- **Phase**: 42 coach-gate-25
- **Blocks**: —
- **Blocked By**: — independent of 130/131/132 (none of the four gate-fix
  tickets block each other); dependent only on the gate-25 base already in
  develop (incl. PAIML-POLE-API-126 WS per-turn guard).

## Context

SAMPLE-5 gate run `app/pole_analyst/test-results/coach-150q/sample5-647d57e-20260921-205203/`
(`coach-150q-judge.md` + `coach-150q-transcript.jsonl`): **COACH7-VA-05 fails**
(empty blocks / empty reply), **COACH7-VA-02 is flaky** (passes in the judge
row but times out on repetition).

### Evidence / root cause
`agent.run timed out after 120.00s` — the 095 ReAct sub-budget
(`build_turn_timeout_turn()` in `services.py`, guard at
`app/pole_api/src/analyst_chatbot/services.py:407-425`) fires **before** the
126 WS per-turn wall-clock guard can complete the turn. A long composed chain
(supergraph brain 30s + ReAct 120s + OpenRouter tail calls) exceeds the 120s
`agent.run` bound first → terminal frame `status: error` +
`error_code: turn_timeout` → the FE maps it to Error and never shows
"Question answered" → spec 360s timeout.

Budget ladder today:

| Budget | Value | Where |
| :--- | :--- | :--- |
| supergraph brain | 30.0 s | `coach_providers.py:95 SUPERGRAPH_TURN_BUDGET_S` |
| ReAct `agent.run` (095) | 120.0 s | `services.py:296/409/416` ← default from `LLM_TIMEOUT` / `CHATBOT_TURN_TIMEOUT` (`config.py:268/271`) |
| WS per-turn guard (126) | 300.0 s | `config.py:97 DEFAULT_ANALYST_WS_TURN_BUDGET_S`, applied `router.py:255+` |
| FE turn budget | 360 000 ms | spec `TURN_BUDGET_MS` |

The 126 guard works (no hang) — but the 120s sub-budget fires first, so the
composed chain never gets the headroom the guard allows.

## Scope (Option A, CHOSEN)

Raise the analyst `agent.run` `max_turn_seconds` from **120 s toward 240 s** —
must remain **BELOW** the WS per-turn wall-clock guard
(`Settings.analyst_ws_turn_budget_s`, default 300.0) and the FE budget
(360 s).

- **Keep timeout = error semantics.** Do **NOT** reclassify
  timeout-with-partial-answer frames to ok/fallback — that is explicitly
  **REJECTED**. The terminal `error` + `error_code: turn_timeout` frame remains
  the contract on expiry.
- Locate the config: search `max_turn_seconds` / `agent.run` in
  `app/pole_api/src/analyst_chatbot` (`services.py` 095 guard, agent wiring).
  The 120 s default comes from settings/env (`LLM_TIMEOUT` /
  `CHATBOT_TURN_TIMEOUT`, `config.py:268/271`) — if it is env-driven, document
  the env var name and add the **ENV_VARS.md** entry requirement.

## Files Affected
- `app/pole_api/src/analyst_chatbot/` — agent `max_turn_seconds` budget
  (settings/env default; wiring that constructs the ReAct agent).
- `docs/ENV_VARS.md` — new/updated row for the ReAct sub-budget env var (if
  env-driven).

## Validation Plan
1. Targeted battery re-run (twice — flakiness must be gone):
   ```bash
   npx playwright test coach-150q.spec.ts --workers=1 -g "COACH7-(VA-02|VA-05)"
   ```
   Must pass **twice in a row**.
2. Backend logs show turns completing < 300 s on the long composed chains
   (no `agent.run timed out` on turns that previously died at 120 s).
3. Full SAMPLE-5 gate **25/25** as phase acceptance (with 130/131/132).

## Acceptance Criteria
- [ ] VA-02 + VA-05 pass in the SAMPLE-5 gate, twice in a row (flakiness gone).
- [ ] Budget ladder preserved: ReAct sub-budget (≤ 240 s) < WS guard
      (`analyst_ws_turn_budget_s`, 300.0) < FE budget (360 s).
- [ ] Timeout keeps `error` + `error_code: turn_timeout` semantics — no
      reclassification of partial-answer frames to ok/fallback.
- [ ] Env var documented (ENV_VARS.md row) if the budget is env-driven.

## Dependencies
- **Blocked By**: — (gate-25 base incl. PAIML-POLE-API-126 already in develop).
- **Blocks**: — (independent of 130/131/132).

## Estimated Effort
- [S]