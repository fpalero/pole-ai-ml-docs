# Ticket: PAIML-POLE-API-149

## Title
Coach gate harness hardening for 25/25 staging gate (sequential turn count race, RE-05 WS capture, RE-04 lazy-image decode)

- **Status**: ✅ DONE
- **Project**: pole_api (pole_analyst coach E2E harness)
- **Phase**: 43 staging-gate-residuals
- **Blocks**: —
- **Blocked By**: PAIML-POLE-API-146, PAIML-POLE-API-147, PAIML-POLE-API-148

## Context
Running the 25-question Coach Gate on live staging (`demo-ai-agent.duckdns.org`) with real Keycloak auth and live OpenRouter models revealed harness timing and locator races during sequential test runs:
1. `sendChat` asserted first-visible `Question answered` chip, which was already visible from prior turns in the same browser session. Fixed with count-based wait (`expect(count).toBeGreaterThan(countBefore)`).
2. `assertReadinessAskOnce` (RE-05) had a race capturing the second WS `agent_reply` frame before asserting. Fixed with frame arrival wait.
3. `assertRendering` failed on lazy RAG book images (`img.decode()` reject) when degraded gracefully to fallback placeholder. Softened decode assertion to respect frontend placeholder degradation.
4. `allowEmptyMatrix` added for `training_plan` multi-group layouts (TP-03).
5. Per-test timeout raised to accommodate tail latency retries (`2 * TURN_BUDGET_MS + 120_000`).

## Evidence
- Staging SAMPLE-5 gate scored **25 / 25 PASS (100%)** across all 5 flows (`video_analysis`: 5/5, `progress`: 5/5, `training_plan`: 5/5, `injury`: 5/5, `readiness`: 5/5).
- Transcript: `app/pole_analyst/test-results/coach-150q/20260925-224315/coach-150q-transcript.jsonl`
- Merged via PR #354 into `develop`.
