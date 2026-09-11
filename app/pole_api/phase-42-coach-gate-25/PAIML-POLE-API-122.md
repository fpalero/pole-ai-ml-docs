# Ticket: PAIML-POLE-API-122

## Title
Coach 25-battery gate: ground all unanswered flows (FC1–FC6) — local-only until 25/25 green

## Status
🟡 IN PROGRESS — local k3s + ollama `qwen3.8:27b` iteration; no PR until the
full `COACH150Q_SAMPLE=5` battery is **25/25 green** locally. Code PR targets
`pole-ai-ml` `develop` (auto-deploys to staging on merge).

## Description
The full SAMPLE-5 battery (2026-09-11T05:57Z, RUN_ID
`sample5-post116-20260911-055758`, staging image `9c88ab0`) scored
**8/25** — GATE FAIL (bar = 5/5 per flow; best flow TP 3/5). All 17 failures
collapse into 6 root-cause classes (FC1–FC6), each with an evidenced code
path. This ticket fixes ALL of them in ONE code PR, validated locally
(k3s + ollama `qwen3.8:27b`, the repo default `LLM_PROVIDER=ollama`) until
the whole battery is green, and only then raises the PR to `develop`.

### The 6 failure classes (evidence: file:line)

**FC1 — Progress answers carry data but no tool proof (PR-01, PR-05).**
Blocks `[md, progress_matrix]` with REAL matrix content (gates, p20 %, deltas
matching seeded snapshots exactly), yet `tool_calls=[]` → the spec's
`get_progress_matrix called` assertion fails. Root cause:
`app/pole_api/src/analyst_chatbot/services.py:326-333` — the supergraph-brain
wrapper hardcodes `tool_calls=[]` when returning the brain's `AgentTurn`,
even though the progress graph reached real data through
`AnalystTrickProgressProvider.get_trick_progress`
(`coach_providers.py:280-301`, which itself calls
`facade.get_progress_matrix`) and emitted a `progress_matrix` block
(`pole_coach/graphs/progress.py` `finish_matrix` via
`graphs/_common.py:76-157`). The provider DID query the real facade — the
tool evidence is dropped at the wrapper. **Fix: publish the truthful tool
calls the brain made** (route through the real `get_progress_matrix` tool /
propagate provider-backed tool evidence) so the spec and downstream
consume real tool proof.

**FC2 — No-context fallback, the biggest lever (8 turns: PR-02/03/04,
RE-01/02/03/05, VA-03).** All eight carry no resolvable `video_id` and the
trick either doesn't resolve or the graph has no retrieval path:
- `_VIDEO_REFERENCE_RE` (`coach_providers.py:101`) matches only
  `video|clip|footage` → VA-03 "last **upload**" never triggers the 115 R2
  latest-analyzed leg (`coach_providers.py:1058-1075`) → `video_id=None` →
  SAFE_FALLBACK ("I couldn't build full coaching advice…", 0 tools).
- Metric-only progress turns ("compare my angular_speed now vs last
  month", "hip_height trend", "wrist_stability vs 2 weeks ago") resolve no
  trick and no video → progress graph's `fetch_trick_progress` skips on
  missing `trick_name` (`_common.py:99-101`) → legacy chain → terminal
  degraded turn.
- Readiness (RE-01/02/03/05): trick resolves (Ayesha/Cocoon/etc.), but the
  readiness graph has **no retrieve node**, so `hasRagProof` is structurally
  impossible → "No metrics are available for this session…" md-only.
  **Fix: extend the matcher to `upload/session/recording`, default
  data-oriented turns to the latest analyzed video (single sort+limit, as
  115 R2), and give readiness a tool-grounded (ReAct) path that yields
  retrieval evidence even when verdict is "can't assess".**

**FC3 — Broken `/api/images/*` (VA-04, TP-03, IN-02).** Otherwise-rich
grounded answers (8/6/5 tools ok) fail ONLY on an unloaded `<img>` with
`?token=`. Root cause: the hash gate at
`analyst_chatbot/blocks.py:352-357` drops only when
`_resolves_image_hash(src) is False`; the **`None` branch** (lazy import
failure `blocks.py:309-310`, resolve exception `316-317`, or TOCTOU between
resolve and browser fetch) passes the raw `/api/images/<hash>` src through,
the endpoint 410s it, and the spec's `broken images` assertion
(`coach-150q.spec.ts:450-461`) fails. Docstring at `blocks.py:302-305`
*documentedly* allows `None` to pass — a deliberate but wrong decision.
**Fix: fail closed — `_resolves_image_hash(src) is not True → drop`; also
validate URLs in `_image_blocks_from_urls` (`answer_shaping.py:268-282`)
before minting blocks. Deep-dive into WHY hashes become unverifiable is a
separate future ticket (PAIML-POLE-API-123).**

**FC4 — WS zero-frame timeouts (VA-05, TP-05, IN-04).** FE `Question
answered` waits `TURN_BUDGET_MS=360s` (`coach-150q.spec.ts:126-132, 316-325`)
but the WS handler has no per-turn wall-clock guard around `run_turn`; the
30s supergraph budget (`SUPERGRAPH_TURN_BUDGET_S`, `coach_providers.py:95`)
+ 120s ReAct budget (`CHATBOT_TURN_TIMEOUT`, `config.py:257`) can chain past
360s with OpenRouter tail calls and never reach a reply → zero `agent_reply`
frames. Mainline cause may vanish on local ollama (fast, no OpenRouter
tail), but the guard is still required so a stuck turn degrades to a
bounded error instead of hanging. **Fix: `asyncio.wait_for` a per-turn wall
clock around `run_turn` in the WS router (settings-driven), producing a
terminal frame on expiry.**

**FC5 — Trick-less injury fallback (IN-03).** "sprained my left wrist…"
names no catalog trick → `make_pole` (needs `trick_name`,
`_common.py:167-172`) skipped → `make_coach` (needs BOTH pole_context AND
biomech_context, `_common.py:256-257`) skipped → `make_finish` with
safety-disclaimer-only md (`_common.py:371-414`) → cross-flow `hasRagProof`
false (bare-LLM). The coach node over-requires: injury turns are answerable
from biomech context + RAG retrieval alone. **Fix: allow the coach node to
run for injury turns on biomech + retrieval when no trick resolves, always
yielding tool evidence.**

**FC6 — Harness ping flake.** `helpers.ts:65-79` `beforeAll` pings
`${API}/health` with `AbortSignal.timeout(900)` + 1s test timeout — killed
run1 server-side over public internet (backend was reachable 3/3 right
after). **Fix: raise the ping budget (e.g. 10s) + one bounded retry.**

### Fix grouping summary (ONE code PR)
1. `coach_providers.py` — extend `_VIDEO_REFERENCE_RE` (upload/session/
   recording), latest-video defaulting for data-oriented turns, propagate
   tool-call evidence from the brain path.
2. `services.py` — brain `AgentTurn` carries real `tool_calls` (FC1); WS
   router per-turn wall-clock guard (FC4).
3. `blocks.py` / `answer_shaping.py` — fail-closed image gate + URL
   validation (FC3).
4. `pole_coach/graphs/_common.py` / `progress.py` / readiness graph —
   biometric-only injury coach (FC5), readiness retrieval evidence (FC2).
5. `app/pole_analyst/e2e/helpers.ts` — ping budget + retry (FC6).

## Files Affected
- `app/pole_api/src/analyst_chatbot/coach_providers.py`
- `app/pole_api/src/analyst_chatbot/services.py`
- `app/pole_api/src/analyst_chatbot/blocks.py`
- `app/pole_api/src/analyst_chatbot/answer_shaping.py`
- `packages/pole_coach/src/pole_coach/graphs/_common.py`
- `packages/pole_coach/src/pole_coach/graphs/progress.py`
- `packages/pole_coach/src/pole_coach/graphs/` (readiness)
- `app/pole_analyst/e2e/helpers.ts`
- tests: per-fix unit tests + `COACH150Q_SAMPLE=5` gate

## Validation Plan (local-first — mandatory)
1. **Local registration:** build images → `localhost:5000`, deploy to
   `k3s-local` (`values-local.yaml`, tags `dev`, `imagePullPolicy: Always`),
   `LLM_PROVIDER=ollama` `OLLAMA_MODEL=qwen3.8:27b`.
2. **Seed:** COACH7-SETUP fixtures in local working DBs (handspring+
   cohort+insights+progress_matrix snapshots).
3. **Loop:** run `COACH150Q_SAMPLE=5` (`workers:1`, 360s/turn, unique
   RUN_ID, `/tmp` transcript backup after every 5 turns) → triage any
   failure's evidence packet → fix → rebuild → redeploy → re-run. Iterate
   until **25/25 green**.
4. **Unit tests:** `pixi run test-api` green (≥80% coverage).
- NEVER run the gate against staging/prod DBs (conftest `_testing` guard;
  local run uses remote-backend mode against the deployed local stack).
5. **PR:** only after local 25/25 — one PR to `pole-ai-ml` `develop`.
   Merge auto-deploys to staging (user-confirmed).

## Unit-Test Requirement
- [ ] FC1: brain `AgentTurn` carries `get_progress_matrix` tool call when a
      `progress_matrix` block is present (and no tool_call is echoed when
      none).
- [ ] FC2: `_VIDEO_REFERENCE_RE` matches upload/session/recording; latest-
      analyzed default fires for metric/cohort/readiness turns; readiness
      graph yields retrieval evidence.
- [ ] FC3: unverifiable hash (None) drops the image block; `_coerce_image_block`
      unit cases for True/False/None.
- [ ] FC4: WS per-turn guard returns a terminal frame past the deadline.
- [ ] FC5: trick-less injury turn produces a grounded answer (tools/retrieval),
      disclaimer present.
- [ ] FC6: helper ping retries once.

## Integration Tests
- [ ] `COACH150Q_SAMPLE=5` gate **25/25 green** on local k3s
      (ollama `qwen3.8:27b`).
- [ ] `pixi run test-api` green.

## Acceptance Criteria
- [ ] Local SAMPLE-5 battery 25/25 green.
- [ ] No regression to currently-passing turns (Q1/Q2 smoke, bank #27).
- [ ] Code PR raised to `pole-ai-ml` `develop` only after local green
      (user-confirmed: merge auto-deploys to staging).

## Dependencies
- **Blocked By**: PAIML-POLE-API-123 (image deep-dive) is FUTURE — NOT
  blocking; FC3 fail-closed fix ships here independently.
- **Blocks**: none.

## Estimated Effort
- [M]