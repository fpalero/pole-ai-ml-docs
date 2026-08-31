# Ticket: PAIML-CREW-005

## Title
Unit tests for guardrails

## Description
Create comprehensive unit tests for the `crew/guardrails.py` module, covering agent wrapping, task validation, and tool result formatting.

## What to Do
- Create `crew/tests/test_guardrails.py` (or `crew/tests/` directory if it doesn't exist)
- Test `apply_guardrails()`:
  - Verify `max_iter` is set to `CREW_MAX_ITER` value
  - Verify `max_rpm` is set to `CREW_MAX_RPM` value
  - Verify it returns the modified agent
  - Test with custom env var values
- Test `validate_dev_output()`:
  - Valid: output contains "diff" or "written" or "test" → returns True
  - Invalid: output has no code evidence → raises ValueError
- Test `validate_review_output()`:
  - Valid: output contains "PASS" or "FAIL" or "verdict" → returns True
  - Invalid: output has no verdict → raises ValueError
- Test `validate_test_output()`:
  - Valid: output contains "TEST_VERDICT: PASS" → returns True
  - Valid: output contains "TEST_VERDICT: FAIL" → returns True
  - Invalid: output has no TEST_VERDICT → raises ValueError
- Test `tool_result()`:
  - `tool_result(True, "ok")` → `"SUCCESS: ok"`
  - `tool_result(False, "fail")` → `"ERROR: fail"`
- Add pytest markers for the new test file
- Ensure tests can run standalone: `pytest crew/tests/test_guardrails.py -v`

## Acceptance Criteria
- [ ] `crew/tests/test_guardrails.py` exists
- [ ] All test functions pass
- [ ] Coverage for `guardrails.py` ≥ 80%
- [ ] Tests cover both valid and invalid inputs for each validator
- [ ] Tests verify env var configurability

## Dependencies
- **Blocked By**: PAIML-CREW-001, PAIML-CREW-002, PAIML-CREW-003, PAIML-CREW-007
- **Blocks**: PAIML-CREW-006, PAIML-CREW-008
