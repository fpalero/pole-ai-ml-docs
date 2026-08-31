# Ticket: PAIML-INFRA-020

## Title
[Backend] Configure structured log environment variables and uvicorn access logs

## Description
Set up environment variables and uvicorn configuration so that all pole_api logs are consistently structured JSON. This includes: (a) `LOG_LEVEL` env var (default INFO), (b) `LOG_SERVICE_NAME` env var (default pole_api) injected into every log record, (c) uvicorn access logger JSON formatting via `LoggingConfig` or `use_logger_config`, and (d) ensure health-check and similar endpoint logs are also JSON.

## What to Do (Implementation Steps)
- [ ] Step 1: Add `LOG_LEVEL` and `LOG_SERVICE_NAME` to the pole_api Dockerfile env defaults (or Helm values) with sensible defaults.
- [ ] Step 2: Update `core/logging.py` to read `LOG_LEVEL` and `LOG_SERVICE_NAME` from `os.environ` and inject them into every log record via a `Filter`.
- [ ] Step 3: Configure uvicorn to use the custom logging config: either `uvicorn.run(..., log_config=...)` or set `LOGGING_CONFIG` env var to disable default uvicorn config and use the pole_api one.
- [ ] Step 4: Verify that `kubectl logs -n pole-ai <pole-api-pod>` shows JSON for both application logs and access logs (first few lines of a request).
- [ ] Step 5: Add a one-line test that `os.environ.get("LOG_SERVICE_NAME")` appears in the emitted log record.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `LOG_LEVEL` and `LOG_SERVICE_NAME` env vars are respected by the logging system.
- [ ] Both application logs and uvicorn access logs are JSON-formatted in `kubectl logs`.
- [ ] `LOG_SERVICE_NAME` value (e.g., `pole_api`) appears in every log record.
- [ ] Health check endpoint logs are also structured JSON.

## Integration Tests to Run (Local Verification)
- [ ] `kubectl logs -n pole-ai <pole-api-pod> | head -5 | python3 -c "import sys, json; [json.loads(l) for l in sys.stdin if l.strip() and 'LOG_SERVICE_NAME' in json.loads(l)['service_name']]"` — should not error.
- [ ] `pixi run test` passes.
- [ ] Manual `kubectl logs` check as described.

## Dependencies
- **Blocks:** PAIML-INFRA-021 (test updates depend on JSON logger + env vars)
- **Blocked By:** PAIML-INFRA-019 (JSON formatter needs to be in place first)

## Estimated Effort
- [M] (Medium < 4h)