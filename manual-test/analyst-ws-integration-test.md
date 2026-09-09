# Analyst Chatbot WS Integration Test (PAIML-POLE-API-092)

- **Ticket:** PAIML-POLE-API-092
- **Test module:** `app/pole_api/tests/test_analyst_ws_integration.py`
- **Stack under test:** LOCAL k3s (`pole-ai` ns) — WS `ws://api.pole.local/api/analyst-chatbot/ws/analyst-chat?token=<JWT>`, Keycloak `https://keycloak.pole.local/realms/pole-ai` token endpoint (client `pole-analyst`, dev/dev, self-signed)
- **Questions evaluated:** 40 (RAG-01..RAG-20 + TOOL-01..TOOL-20) + 1 auth/handshake test = **41 tests**
- **Result:** ✅ **41 passed in ~9.5 min** against the local stack
- **Companion doc:** `docs/manual-test/analyst-agent-test-results.md` (PAIML-POLE-API-091, 20-question manual RAG evaluation — already in the RAG, 96 chunks)

> This page is the reference for the analyst WS integration test 40 questions
> battery (RAG-01..RAG-20 knowledge questions plus TOOL-01..TOOL-20 tool
> questions, 41 tests total with the auth/handshake check).

## Analyst WS integration test — 40 questions

The analyst WS integration test runs 40 questions (20 RAG + 20 TOOL) plus
the auth/handshake check over fresh WS sessions against the local stack.

## Purpose

Live contract battery for the analyst chatbot slice: Keycloak auth → WS
handshake → send question → `agent_reply` with typed answer blocks. It locks
in the FE chat-card `blocks` contract, the expected tool routing, and the
graceful-degradation behaviour when the local video corpus is empty — so the
ordinary unit run stays green without the stack (auto-skip) while the full
battery guards regressions when the stack is up.

## Quick how-to-run

```bash
# from app/pole_api (pytest.ini registers the `integration` marker)
pixi run test-api tests/test_analyst_ws_integration.py -k analyst_ws
# equivalent: pixi run test-api -m integration -k analyst_ws
```

- Per-question timeout default: **240 s** (override via `POLE_ANALYST_TIMEOUT`).
- Full battery takes **~9.5 min** against the local stack (40 fresh WS
  sessions + 1 handshake + 1 corpus probe).

## Environment variables

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `POLE_ANALYST_WS_URL` | `ws://api.pole.local/api/analyst-chatbot/ws/analyst-chat` | WS endpoint (token appended as `?token=<JWT>`) |
| `POLE_ANALYST_AUTH_URL` | `https://keycloak.pole.local/realms/pole-ai/protocol/openid-connect/token` | Keycloak password-grant token endpoint (self-signed; test disables hostname/cert check) |
| `POLE_ANALYST_CLIENT_ID` | `pole-analyst` | Keycloak client id |
| `POLE_ANALYST_USER` | `dev` | Test user |
| `POLE_ANALYST_PASSWORD` | `dev` | Test password |
| `POLE_ANALYST_TIMEOUT` | `240` | Seconds per question (`run_question` loop budget; also the `duration_s < TIMEOUT` assertion) |
| `POLE_SKIP_ANALYST_WS` | _(unset)_ | Set to `1` to force-skip the whole module |

## The 40-question index

### RAG questions (RAG-01..RAG-20) — must always return substantive, non-fallback prose

| QID | Group | Question (verbatim) | Expected tool | Expected blocks | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| RAG-01 | biomechanics | What are the key phases of a handspring in pole dance, from init to exit? | — | — | — |
| RAG-02 | biomechanics | What kinematic markers indicate a technically sound ayesha hold? | — | — | — |
| RAG-03 | biomechanics | How does shoulder engagement change through the different phases of a handspring? | — | — | — |
| RAG-04 | biomechanics | What biomechanical cues suggest a video shows a clean or sloppy phasic execution? | — | — | — |
| RAG-05 | psychology | How should I mentally prepare before attempting a new high-risk trick? | — | — | — |
| RAG-06 | psychology | What are common psychological barriers when training inverted tricks under pressure? | — | — | — |
| RAG-07 | psychology | How can visualization improve my performance consistency in pole competition? | — | — | — |
| RAG-08 | psychology | What mental strategies help recover confidence after a failed trick attempt? | — | — | — |
| RAG-09 | tricks | List the main categories of pole tricks and a representative move for each. | — | — | — |
| RAG-10 | tricks | What is the difference between a handspring and a shoulder mount entry? | — | — | — |
| RAG-11 | tricks | How should a beginner progress step by step toward their first invert? | — | — | `known_transient=True` — hit the fallback once on first run, OK on retry (same transient seen in PAIML-POLE-API-091 Q11) |
| RAG-12 | tricks | What safety considerations matter when training static vs spinning pole? | — | — | — |
| RAG-13 | anatomy | Which muscle groups are primary movers in a deadlift invert? | — | — | — |
| RAG-14 | anatomy | How does grip strength training transfer to pole moves like cup grips? | — | — | — |
| RAG-15 | anatomy | What shoulder mobility drills reduce injury risk for extended holds? | — | — | — |
| RAG-16 | anatomy | What core work best supports ayesha and handspring progressions? | — | — | — |
| RAG-17 | intersection | How do physiological fatigue markers interact with mental focus during long training sessions? | — | — | — |
| RAG-18 | intersection | What training split balances strength, flexibility, and skill practice for an intermediate? | — | — | — |
| RAG-19 | intersection | How should warm-ups combine mobility and mental activation before a high-risk trick session? | — | — | — |
| RAG-20 | intersection | What role does breathing technique play in both physical execution and mental composure? | — | — | — |

Same 20 questions as the PAIML-POLE-API-091 manual evaluation (see
`analyst-agent-test-results.md` for the accepted reply texts).

### TOOL questions (TOOL-01..TOOL-20) — tool registry + FE answer formats

| QID | Group | Question (verbatim) | Expected tool | Expected blocks | Requires video data |
| :--- | :--- | :--- | :--- | :--- | :--- |
| TOOL-01 | tool-list | What videos do I have available for analysis? | `list_videos` | — | No (this is the corpus probe) |
| TOOL-02 | tool-histogram | Show me the trick histogram for my ayesha video. | `histogram` | `md` | Yes |
| TOOL-03 | tool-classify | What trick does my handspring video show? | `classify` | — | Yes |
| TOOL-04 | tool-frames | Extract 6 frames from my handspring video so I can review the entry. | `extract_frames` | `image` | Yes |
| TOOL-05 | tool-crop | Can you crop the first 3 seconds of my handspring video? | `crop` | `video_segment` | Yes |
| TOOL-06 | tool-crop | Crop the segment from second 4 to 7 of my ayesha video (the execution phase). | `crop` | `video_segment` | Yes |
| TOOL-07 | tool-insights | Give me coach insights for my handspring video. | `get_coach_insights` | `md` | Yes |
| TOOL-08 | tool-segment | What happened during the execution phase (seconds 2-6) of my handspring video? | `segment_insight` | `video_segment`, `md` | Yes |
| TOOL-09 | tool-compare | Did I improve compared to my last ayesha session? | `compare_sessions` | `md` | Yes |
| TOOL-10 | tool-cohort | Where do I stand versus other athletes on the handspring? | `cohort_percentiles` | `md` | Yes |
| TOOL-11 | tool-plan | Build me a 4-week improvement plan to master the ayesha. | `improvement_plan` | `md`, `drills` | Yes |
| TOOL-12 | tool-deepdive | Why is my torso tilt (M-05) off at second 3 of the handspring video? | `metric_deep_dive` | `metric_matrix`, `video_segment` | Yes |
| TOOL-13 | tool-frame | What exactly is wrong at frame 45 of my handspring video? | `frame_pose` | `video_segment` | Yes |
| TOOL-14 | tool-trend | Am I plateauing on M-01 angular speed across my handspring sessions? | `progress_trend` | `md` | Yes |
| TOOL-15 | tool-focus | What should I focus on during my next session? | `focus_recommendation` | `md` | Yes |
| TOOL-16 | tool-risk | Scan my handspring video for injury risks. | `risk_scan` | `md` | Yes |
| TOOL-17 | tool-summary | Read me the coach summary for my handspring video. | `get_coach_summary` | `md` | Yes |
| TOOL-18 | tool-pose | Show me the critical pose from the coach breakdown of my handspring video. | `get_coach_pose` | `image` | Yes |
| TOOL-19 | tool-format-mixed | Give me a score summary and quick follow-up exercises for that pose. | _(any tool)_ | `score_summary`, `quick_replies` | Yes |
| TOOL-20 | tool-compare-baseline | Compare the metrics between my handspring video and my latest ayesha video. | `compare_sessions` | `metric_matrix`, `md` | Yes |

Plus `test_analyst_ws_auth_and_handshake` (Keycloak token → WS `connected`
frame with `ws_connection_id`).

## Assert semantics

### Blocks contract (FE chat-card)

- Allowed `type` values (mirror `analyst_chatbot/blocks.py`):
  `md`, `video_segment`, `analysis_link`, `image`, `score_summary`,
  `phasic_feedback`, `metric_matrix`, `drills`, `quick_replies`.
- Per-type field checks in `validate_blocks`: `md` needs non-empty
  `content`; `video_segment` needs `video_id`; `image` needs `src`;
  `score_summary` needs int `score`; `metric_matrix` needs `rows` list;
  `drills` needs `items` list; `quick_replies` needs `replies` list;
  `phasic_feedback` needs `items` list. Unknown types and non-object
  entries fail.
- The test validates the **`blocks` frame field** (the typed list the FE
  renders) when present: must be a non-empty list, all blocks valid, and —
  when the corpus is populated — the question's `expected_blocks` subset
  must be present. `reply`-embedded JSON arrays are tolerated via
  `parse_blocks` (raw `json.loads`, falling back to `raw_decode` for
  trailing prose) but only surfaced as a `RuntimeWarning` (see below), not
  a failure.
- Fallback detection: any reply containing `I'm having trouble
  understanding. Please try again with a shorter description.` (or
  `trouble understanding`) fails — except RAG-11 (`known_transient`),
  which is exempt from the fallback assertion.

### Fresh-session guard (context-saturation)

- The `analyst_session` fixture is a **factory that opens a FRESH WS
  session per question** (`open_session` → assert `connected` +
  `ws_connection_id` → send → collect until `agent_reply` → close).
- Rationale: the PAIML-POLE-API-091 side observation showed single-session
  runs degrade to fallback after ~15 turns (Q16–Q20 fast-failed at 1–7 s
  via the rephrase-budget fast-fail); fresh sessions avoid that saturation.
- `run_question` sends `{"type": "message", "message": ..., "client_timestamp": ...}`
  and collects until the `agent_reply` frame (`reply` + `tool_calls`), then
  asserts `duration_s < TIMEOUT`.

### Corpus-empty graceful-degradation mode

- The session-scoped `corpus_available` fixture probes with TOOL-01
  (`list_videos`): corpus is available only if the tool ran AND the reply
  contains none of `no videos / no video / none available / haven't
  uploaded / have not uploaded`.
- When `require_video_data=True` and the corpus is **empty**, format
  assertions relax: `expected_blocks` presence is skipped, and the
  `expected_tool` assertion degrades to "tool call + clean relay, OR
  substantial prose (≥ 80 chars)". Corrupt/empty replies and fallbacks
  (outside RAG-11) still fail.
- TOOL-01 itself always asserts the tool call (it is the probe, not gated).

### Auto-skip ("always usable")

- Module-level skip when `POLE_SKIP_ANALYST_WS=1` **or** the WS host:port
  TCP probe (`_stack_reachable`, 2 s) fails — so `pixi run test-api`
  stays green without the stack. Missing `websocket-client` also skips.

## Known warnings (non-fatal)

- **`reply` raw-JSON RuntimeWarning (one per question):** the deployed API
  pod (2 days 19 h old at run time) sends the raw LLM JSON block array in
  the `reply` field — prose normalization exists on `develop` but was not
  yet deployed. Non-fatal by design; the FE renders `blocks`. The warning
  text is `<qid>: 'reply' field contains a raw JSON block array (prose
  normalization not active on this deployment)`. It disappears once the
  normalization ships.
- **Redis pool thread warning:** app noise from the API process (connection
  pool background thread), unrelated to this battery — safe to ignore.

## Latest result

- **41 passed** (auth/handshake + 40 questions) in **~9.5 min** against the
  local k3s stack, with the per-question raw-JSON `RuntimeWarning` notes
  described above.
- Rerun with `pixi run test-api tests/test_analyst_ws_integration.py -k analyst_ws`
  from `app/pole_api` after the prose-normalization deploy to confirm the
  warnings clear and the battery stays green.
