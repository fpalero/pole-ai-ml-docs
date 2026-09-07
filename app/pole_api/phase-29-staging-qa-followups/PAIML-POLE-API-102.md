# Ticket: PAIML-POLE-API-102

## Title
[Chatbot] Gate-3 residual: TOOL-08 segment-insight trace + fix, wire shaping (empty-slot joins + nested-block double-encode), empty-input graceful nudge

## Description
Phase 29 — see [PLAN_PHASE_29](../plan/PLAN_PHASE_29.md). Gate-3 residual from
the staging QA gate-3 battery (tester evidence, local, not committed):
`/tmp/opencode/staging-gate3/` (`TOOL-08.json`, `TOOL-04.json`,
`TOOL-10.json`, `TOOL-19.json`, `TOOL-20-SUB.json`, `RAG-06.json`,
`RAG-10.json`, `RAG-12.json`, `RAG-13.json`, `_FINAL_TALLY.json`,
`_summary.json`; repro script `/tmp/opencode/gate3_battery.py`, exploratory
probes `/tmp/opencode/gate3_exploratory.py`). Tally: 23/24 green with TOOL-08
the single RED (`_summary.json`: `"failed": ["TOOL-08"]`).

Tester triage recs (verbatim — the three items below):

### 1. TOOL-08 trace + fix
"What happened during the execution phase (seconds 2-6) of my handspring
video?" → 3/3 non-answers over ~10h (095-deadline message +
video_segment-only; thin 138ch relay; fallback + tools). Expected
`segment_insight` + md phase narrative. Suspect segment-result vs 097
retry-budget interaction swallowing the result.

Captured variant (fallback + tools) in `TOOL-08.json`: reply is the generic
`"I'm having trouble understanding. Please try again with a shorter
description."` plus a `video_segment` block (handspring `6a9e65ef…`, frames
60–119) and a `metric_matrix` hip_height deep dive; `checks.no_fallback` is
false → `pass: false` (dur 96.39s; tools `list_videos`, `segment_insight`,
`query_biomechanics`, `query_pole`, `query_calisthenics`, `crop`,
`metric_deep_dive` ×2 — the tools ran, the narrative never arrived).

Exact WS repro (from `gate3_battery.py::run_one`, same stack the FE uses):

```
# 1. Mint token (Keycloak password grant)
POST https://pole-keycloack.duckdns.org/realms/pole-ai/protocol/openid-connect/token
  client_id=pole-analyst, grant_type=password, username=dev, password=dev, scope=openid
# 2. Open the analyst chatbot socket
wss://pole-coach.duckdns.org/api/analyst-chatbot/ws/analyst-chat?token=<access_token>
# 3. Expect {"type":"connected"}, then send:
{"type":"message","message":"What happened during the execution phase (seconds 2-6) of my handspring video?","client_timestamp":<now>}
# 4. Wait for {"type":"agent_reply"} (battery TIMEOUT=240s)
```

### 2. Wire shaping
Strip `[, , …]` empty-slot joins in md prose (user-visible in TOOL-04/10/19/20:
`TOOL-04.json` has `"…handspring_test.mp4…:\n[,\n,\n,\n,\n,\n]\n…"`,
`TOOL-10.json` has `"…comparison.\n\n[, , ]\n…"`, `TOOL-19.json`
`[, , , , , , , ]`, `TOOL-20-SUB.json` `[, , , ]`) + kill nested `[{…}]`-in-md
double-encode (`RAG-06`/`10`/`12`/`13` wire replies start with the literal
`[{"type": "md", "content": "…` — block JSON nested inside md prose; FE
normalizes today, contract must hold at wire layer). Likely 096 shaping-list
joins — verify-before-fix.

### 3. Empty-input graceful prompt
`""` currently yields silence (no `agent_reply`; exploratory Case A-empty
WARNING in `gate3_exploratory.py`). Require a graceful nudge reply instead.

## What to Do (Implementation Steps)
- [ ] (1) **Server-side trace FIRST, then fix.** Reproduce via the exact WS
  repro above against staging; trace the TOOL-08 turn server-side
  (`segment_insight` result path vs the 097 blank-retry budget vs the 095
  turn-deadline path) and identify where the segment result is dropped or
  swallowed. Then fix so the turn answers with `segment_insight` + md phase
  narrative (never the 095-deadline message alone, never a thin relay, never
  the generic fallback when the tools succeeded).
- [ ] (2) Verify the shaping source (likely the 096 shaping-list joins) BEFORE
  fixing; then strip the empty-slot joins from md prose and kill the nested
  `[{…}]`-in-md double-encode at the wire layer (FE normalization stays as a
  safety net, not the contract).
- [ ] (3) Empty-input (`""`) returns a graceful nudge `agent_reply` (short
  prompt asking what the athlete needs) — never silence, never a hang.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] (1) TOOL-08 answers with `segment_insight` + md phase narrative across
  reruns (no 095-deadline-message-only, no thin relay, no generic fallback
  when tools succeeded); the trace names the drop point and the fix addresses it.
- [ ] (2) TOOL-04/10/19/20 md prose contains no `[, , …]` empty-slot joins;
  RAG-06/10/12/13 wire replies contain no nested `[{…}]` block JSON inside md
  (contract holds at the wire layer).
- [ ] (3) `""` yields a non-empty graceful-nudge `agent_reply` (no silence, no hang).
- [ ] Staging re-verify: TOOL-08 + the 4 placeholder questions (TOOL-04,
  TOOL-10, TOOL-19, TOOL-20-SUB) green, no regressions in the gate-3 battery.
- [ ] `pixi run test-api` + `pixi run test-chatbot` green, coverage ≥ 80%.

## Integration Tests to Run (Local Verification)
- [ ] Staging rerun of the gate-3 battery (`/tmp/opencode/gate3_battery.py`) +
  exploratory probes (`/tmp/opencode/gate3_exploratory.py`, Case A-empty).
- [ ] `pixi run test-api` and `pixi run test-chatbot` (guarded `_testing` DBs).

## Dependencies
- **Blocks**: None (backend-only; FE already renders md/video_segment/metric
  blocks and the 093(d) error state via `PAIML-POLE-ANALYST-073`).
- **Blocked By**: None. Evidence paths above are local tester artifacts.
  Related: `PAIML-POLE-API-095` (turn deadline bounds the trace/fix —
  deadline-expiry stays distinguishable; no new contracts),
  `PAIML-POLE-API-096` (shaping source — verify-before-fix),
  `PAIML-POLE-API-097` (retry-budget interaction suspect — reuse its error
  signal), `PAIML-POLE-ANALYST-073` (FE error UI, unchanged).

## Estimated Effort
- [S]
