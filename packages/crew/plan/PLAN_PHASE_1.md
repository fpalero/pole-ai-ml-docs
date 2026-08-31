# Phase 1 — Guardrails (anti-infinite-loop)

## Scope

Prevent CrewAI agents from getting trapped in infinite loops by implementing structural and
algorithmic guardrails. This is a defensive improvement to the `crew/` dev-tooling engine.

## Architectural Context

The CrewAI engine (`crew/crew_implement.py`) currently has some guardrails:
- `IMPROVEMENT_ROUNDS = 3` — caps bug-fix iterations
- `REVIEW_RETRIES = 3` — caps `/oc review` re-posts
- `PR_CHECK_TIMEOUT_S = 900` — caps PR merge wait

**Missing guardrails:**
- No `max_iter` on agents (circuit breaker for reasoning loops)
- No `max_rpm` on agents (rate limiter for API spam)
- No task-level validation functions (output quality gates)
- No explicit tool success states (ambiguous feedback causes loop drift)

## Tasks

### Task 1: Create `crew/guardrails.py` module
- Environment variable configuration: `CREW_MAX_ITER` (default: 3), `CREW_MAX_RPM` (default: 15)
- `apply_guardrails(agent)` — sets `max_iter` and `max_rpm` on an agent
- `validate_dev_output(output)` — checks output contains code evidence
- `validate_review_output(output)` — checks output contains PASS/FAIL verdict
- `validate_test_output(output)` — checks output contains `TEST_VERDICT:`
- `tool_result(success, message)` — returns `"SUCCESS: ..."` or `"ERROR: ..."` prefixed string

### Task 2: Refactor tools in `crew_implement.py`
- Use `tool_result()` in `read_file`, `write_file`, `run_shell`, `list_files`, `run_tests`
- Each tool returns deterministic `SUCCESS:` / `ERROR:` messages

### Task 3: Apply guardrails to agents + tasks
- Call `apply_guardrails()` on all 5 agents after creation
- Add `guardrail=` parameter to `dev_task`, `review_task`, `test_task`

### Task 4: Apply guardrails to `crew_phase_end.py`
- Import and apply the same guardrails module
- Ensure consistency across both workflows

### Task 5: Unit tests
- Test `apply_guardrails()` sets correct attributes
- Test each validator function with valid/invalid outputs
- Test `tool_result()` formatting
### Task 6: Documentation update

- Update `crew/README.md` with new env vars and guardrail behavior

### Task 7 (prerequisite): Fix `detect_project` for `docs/packages/`

- Make `crew_implement.detect_project()` recognize the plural `packages` segment (alongside `app`
  and `package`) so tickets under `docs/packages/<project>/...` load correctly. Without this, the
  crew engine (including `crew-validate`) cannot load any package ticket — including its own.

## Dependencies

- `PAIML-CREW-007` (detect_project fix) is a prerequisite so the phase's own tickets are loadable.
- Otherwise standalone.

## Acceptance Criteria

- [ ] `CREW_MAX_ITER` and `CREW_MAX_RPM` env vars work
- [ ] All 5 agents have guardrails applied
- [ ] All tools return `SUCCESS:` / `ERROR:` prefixed messages
- [ ] Task validators catch missing requirements
- [ ] Both workflows (implement + phase-end) use guardrails
- [ ] `detect_project()` recognizes `docs/packages/` (prerequisite fix)
- [ ] Unit tests pass with ≥80% coverage
- [ ] README documents new env vars

## Integration Tests to Run

- UC-01: Run `pixi run crew-validate` on a test tickets folder — should pass
- UC-02: Verify agents respect `max_iter=3` by checking CrewAI logs
- UC-03: Verify tools return deterministic success/error messages
