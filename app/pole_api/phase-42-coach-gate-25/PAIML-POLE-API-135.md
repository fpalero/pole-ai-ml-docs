# Ticket: PAIML-POLE-API-135

## Title
Blank-retry on ABANDONED turns (VA-05 + flaky VA-02): detect degenerate/blank model output and retry/repair instead of finalizing ABANDONED

- **Status**: 📋 PLANNED
- **Project**: pole_api (analyst graph)
- **Phase**: 42 coach-gate-25
- **Blocks**: —
- **Blocked By**: — independent of 134/136/137.

## Context

Phase-42 gate iteration 3 (final): RED 19/25. VA-05 blank-exhaustion (+ flaky
VA-02). Evidence: targeted-129 logs show LLM 200s with `timeout=240.0s` never
firing, `duration=110-171s status=ABANDONED`, transcript `blocks: [] reply: ""`.
The turn finalizes ABANDONED on the first blank/degenerate model output instead
of retrying. Related: 129 raised the ReAct sub-budget; the 240s/300s/360s ladder
stays intact.

USER DECISIONS (binding): no mock data — real performances via pole_fe
(handspring + Shoulder Mount only). Absence of data is tested behavior, not a
setup failure (applies to readiness; VA here is blank-output robustness).

## Scope

Detect degenerate/blank model output in the analyst graph and retry/repair
(re-prompt or grounded fallback) instead of finalizing ABANDONED:

- Blank detector: empty `blocks` + empty `reply` (and equivalent degenerate
  shapes) after an LLM 200.
- On blank: retry the turn step (re-prompt; bounded retries, backoff) or emit a
  grounded fallback — never finalize ABANDONED on the first blank.
- Keep the 240s/300s/360s ladder intact (no budget changes in this ticket).

## Validation Plan
1. Targeted battery, repeated runs (stability):
   ```bash
   npx playwright test coach-150q.spec.ts --workers=1 -g "COACH7-(VA-02|VA-05)"
   ```
   Stable across runs.
2. Logs: blank outputs trigger retry/repair; ABANDONED appears only when all
   retries return blank (genuine failure).

## Acceptance Criteria
- [ ] `-g "COACH7-(VA-02|VA-05)"` stable across runs (VA-05 passes, VA-02 flake
      gone).
- [ ] ABANDONED only on genuine failures (all retries blank), never on first
      blank.
- [ ] 240s/300s/360s ladder intact (no timeout/budget changes).
- [ ] No mock/seeded model output; retries use the live LLM path.

## Dependencies
- **Blocked By**: —.
- **Blocks**: —.

## Estimated Effort
- [S]
