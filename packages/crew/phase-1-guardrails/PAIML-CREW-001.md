# Ticket: PAIML-CREW-001

## Title
Guardrails module

## Description
Create `crew/guardrails.py` — a standalone module implementing CrewAI agent guardrails to prevent infinite loops. This module is reusable across both the `crew-implement` and `crew-phase-end` workflows.

## What to Do
- Create `crew/guardrails.py` with:
  - Environment variable configuration:
    - `CREW_MAX_ITER` (default: `3`) — hard limit on agent reasoning iterations
    - `CREW_MAX_RPM` (default: `15`) — max LLM requests per minute
  - `apply_guardrails(agent)` function:
    - Takes a CrewAI `Agent` instance
    - Sets `agent.max_iter = CREW_MAX_ITER`
    - Sets `agent.max_rpm = CREW_MAX_RPM`
    - Returns the modified agent
  - Task validation functions:
    - `validate_dev_output(output: str) -> bool` — raises `ValueError` if output lacks code evidence (no diff, no file writes, no test results)
    - `validate_review_output(output: str) -> bool` — raises `ValueError` if output lacks PASS/FAIL verdict or findings
    - `validate_test_output(output: str) -> bool` — raises `ValueError` if output lacks `TEST_VERDICT: PASS` or `TEST_VERDICT: FAIL`
  - `tool_result(success: bool, message: str) -> str` helper:
    - Returns `f"SUCCESS: {message}"` when `success=True`
    - Returns `f"ERROR: {message}"` when `success=False`
- Add module docstring explaining the guardrail strategy
- Add type hints to all functions

## Acceptance Criteria
- [ ] `crew/guardrails.py` exists and is importable
- [ ] `CREW_MAX_ITER` defaults to 3, `CREW_MAX_RPM` defaults to 15
- [ ] `apply_guardrails()` sets both attributes on the agent
- [ ] Each validator raises `ValueError` with descriptive message on invalid output
- [ ] `tool_result()` returns correctly prefixed strings

## Dependencies
- **Blocked By**: PAIML-CREW-007
- **Blocks**: PAIML-CREW-002, PAIML-CREW-003, PAIML-CREW-004, PAIML-CREW-005, PAIML-CREW-008
