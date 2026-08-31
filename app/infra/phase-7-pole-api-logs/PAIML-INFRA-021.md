# Ticket: PAIML-INFRA-021

## Title
[Backend] Update caplog tests and add JSON format verification

## Description
The `python-json-logger` change modifies stdout output format. Existing tests that use `caplog` at the `Logger` level should continue to work because `caplog` captures `LogRecord` attributes, not formatted string output. However, add a new test that explicitly verifies the JSON format of log output, ensuring the structured logging change is verified and documented.

## What to Do (Implementation Steps)
- [ ] Step 1: Review existing `caplog` usages in `tests/` — confirm they access `record.getMessage()` or `record.levelno` etc., which are format-agnostic, and update any that inspect `record.message` expecting plain text.
- [ ] Step 2: Add a new test file or test function `test_log_json_format.py` (or similar) that:
   - Configures the logger as the production setup does.
   - Emits a test log message.
   - Captures stdout and asserts the output is valid JSON.
   - Asserts the presence of required fields (`time`, `level`, `name`, `service_name`).
- [ ] Step 3: Run the new test and confirm it passes.
- [ ] Step 4: Run `pixi run test` suite-wide to confirm no regressions.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Existing `caplog`-based tests still pass unchanged (or have been minimally updated).
- [ ] New test `test_log_json_format` passes and validates JSON output structure.
- [ ] `pixi run test` full suite reports ≥80% coverage and no failures.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test` — all tests pass.
- [ ] New test function runs and validates JSON format.

## Dependencies
- **Blocks:** None (standalone verification; depends on PAIML-INFRA-019/020 being applied first so the logger is configured).
- **Blocked By:** None (can be done in parallel with other phase-7 tickets once the logger is configured).

## Estimated Effort
- [S] (Small < 1h)