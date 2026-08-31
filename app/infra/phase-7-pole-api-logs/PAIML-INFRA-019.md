# Ticket: PAIML-INFRA-019

## Title
[Backend] Add python-json-logger dependency and configure JSON formatting in pole_api

## Description
Add the `python-json-logger` package as a dependency of the pole_api service. Replace the default `logging.basicConfig` in the pole_api entrypoint with a JSON formatter that emits structured logs including timestamp, level, logger name, service name, and request ID (when available). Ensure all module-level loggers in pole_api inherit the JSON output format.

## What to Do (Implementation Steps)
- [ ] Step 1: Add `python-json-logger>=2.0` to pole_api `pyproject.toml` dependencies.
- [ ] Step 2: Create a `core/logging.py` module that configures a `logging.Formatter` using `JsonFormatter` (from python-json-logger) with fields: `time`, `level`, `name`, `module`, `funcName`, `lineno`, `message`, `service_name` (set via env var).
- [ ] Step 3: In `main.py`, replace the root `basicConfig` call with configuration from `core.logging.py` (handler with `JsonFormatter`, level from `LOG_LEVEL` env, default INFO).
- [ ] Step 4: Update all existing module loggers (e.g., `analysis`, `crawler`, `video`, `tools`) to use the configured root logger; ensure no logger has its own `basicConfig`.
- [ ] Step 5: Run `pixi run test` and verify existing `caplog` tests still pass (caplog captures record attributes, not formatted output, so they should be unaffected).
- [ ] Step 6: Add a quick verification script that logs a test message and asserts the output contains `"service_name"` and is valid JSON.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `python-json-logger` is installed and importable in the pole_api environment.
- [ ] Root logger outputs JSON-formatted lines to stdout (visible in `kubectl logs`).
- [ ] All module-level logger calls produce JSON output with at minimum: `time`, `level`, `name`, `message`.
- [ ] `pixi run test` passes with no new failures.
- [ ] A verification script confirms JSON output includes `service_name` field.

## Integration Tests to Run (Local Verification)
- [ ] `kubectl logs -n pole-ai <pole-api-pod> | head -3` and verify JSON output (e.g., using `python3 -c "import json, sys; [json.loads(l) for l in sys.stdin if l.strip()]"`).
- [ ] `pixi run test` — full test suite passes.
- [ ] Verification script: `python3 -c "..."` exercises the logger.

## Dependencies
- **Blocks:** PAIML-INFRA-020 (env var + access log config needs JSON logger in place)
- **Blocked By:** PAIML-INFRA-016 (ES running; logging format change independent of ES, but verification benefits from ES+Kibana)

## Estimated Effort
- [M] (Medium < 4h)