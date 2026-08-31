# Ticket: PAIML-CREW-006

## Title
Documentation update

## Description
Update `crew/README.md` to document the new guardrail env vars (`CREW_MAX_ITER`, `CREW_MAX_RPM`) and explain the guardrail behavior.

## What to Do
- Add to the "Env knobs" section in `crew/README.md`:
  - `CREW_MAX_ITER` (default `3`) — hard limit on agent reasoning iterations; circuit breaker for reasoning loops
  - `CREW_MAX_RPM` (default `15`) — max LLM requests per minute; rate limiter for API spam
- Add a new section "## Guardrails" explaining:
  - What guardrails are implemented (agent limits, task validation, tool success states)
  - How they prevent infinite loops
  - How to configure them via env vars
  - Which tasks have validation (dev → code evidence, review → verdict, test → TEST_VERDICT)
- Update the "Flow 1" description to mention that agents have `max_iter` and `max_rpm` applied
- Verify the README renders correctly (no broken markdown)

## Acceptance Criteria
- [ ] `CREW_MAX_ITER` and `CREW_MAX_RPM` documented in Env knobs table
- [ ] New "Guardrails" section explains the anti-infinite-loop strategy
- [ ] Flow 1 description mentions guardrails
- [ ] No broken markdown or formatting issues

## Dependencies
- **Blocked By**: PAIML-CREW-005
- **Blocks**: PAIML-CREW-008
