# Ticket: PAIML-CREW-008

## Title
Integration tests: guardrails + local Ollama

## Description
Add an **integration test suite** for the CrewAI guardrails used by the implementation
and phase-end flows, calling **local Ollama** (`http://localhost:11434`, model
`qwen3.8:27b`). This closes the loop opened by the unit tests (`test_guardrails.py`,
`test_llm.py`): the unit tests verify the guardrail *logic* in isolation with mocks,
while this suite verifies the guardrails actually function against a **real LLM
runtime**, proving they prevent runaway loops and consume no more than the configured
iteration/rate limits.

Every acceptance criterion from phase-1 tickets PAIML-CREW-001..007 that is observable
at runtime must be exercised here end-to-end (see "Phase Acceptance Coverage" below).

## Prerequisites
- Local Ollama reachable at `http://localhost:11434` with model `qwen3.8:27b` pulled.
  (Confirmed available: `qwen3.8:27b`, `qwen3-coder:30b`, `qwen3-coder:latest`,
  `gpt-oss-agent:latest`, `deepseek-r1-lite:latest`.)
- `crew/llm.py` already supports `provider="ollama"` → `LLM(model='openai/qwen3.8:27b',
  base_url='http://localhost:11434/v1', api_key='ollama')`. Verified working end-to-end
  (real call returned `HOLA`).

## What to Do

Create `crew/tests/test_integration_ollama.py` with pytest markers
`@pytest.mark.integration` and `@pytest.mark.ollama`. All tests must:

1. **Skip cleanly when Ollama is unreachable** — use a module-level fixture that pings
   `http://localhost:11434/api/tags` (short timeout) and `pytest.skip(...)` when offline.
   Never fail the suite on an environment that lacks Ollama; the suite is opt-in via
   `-m integration`.
2. **Build the LLM from the real factory** — `build_llm(provider="ollama")` returns
   `(llm_flash, llm_pro)`; assert the model is `openai/qwen3.8:27b`, base URL ends in
   `/v1`, and api key is `ollama` (mirrors PAIML-CREW-001 factory contract).
3. **Exercise the guardrail validators against real LLM output**:
   - Run a real Ollama call and feed its output through `apply_guardrails`, then run a
     dev-style task output through `validate_dev_output`, `validate_review_output`, and
     `validate_test_output`. Assert the output carries code/verdict/test evidence or that
     the validator raises `ValueError` with a descriptive message — covering
     PAIML-CREW-001 / PAIML-CREW-003 acceptance (validators reject no-evidence output).
<<<<<<< Updated upstream
4. **Prove `max_iter` / `max_rpm` are honoured at runtime** (PAIML-CREW-003 / PAIML-CREW-004):
=======
4. **Prove `max_iter` / `max_rpm` are honoured at runtime** (PAIML-CREW-003 / -004):
>>>>>>> Stashed changes
   - Build a small CrewAI `Agent` (or a minimal stub exposing `max_iter`/`max_rpm`), run
     `apply_guardrails(agent)`, then execute a real crew/agent loop against Ollama with
     `CREW_MAX_ITER` set low (e.g. 2) and assert the loop terminates within the bound
     (i.e. no infinite loop; iteration count ≤ configured max, including self-correction
     that the guardrail permits).
   - Assert the LLM request rate does not exceed `CREW_MAX_RPM` over a short window.
5. **Verify the crew-implement wiring** (PAIML-CREW-003): after importing
   `crew_implement.build_crews`, assert all 5 agents have `max_iter`/`max_rpm` set from
   `apply_guardrails`, and that dev/review/test tasks carry the correct `guardrail=`
   validator (the integration run executes at least one dev→review→test round against
   Ollama and asserts each validator ran).
6. **Verify the phase-end battery honours the provider** (PAIML-CREW-004): drive
   `crew_phase_end`'s `run_ticket_integration`-style command with `provider="ollama"` and
   assert it resolves and executes (this wires the `--provider ollama` flag already
   present in `crew_phase_end.py`).

## Phase Acceptance Coverage (must all be exercised by the integration run)

| Ticket | Criterion exercised here |
| :--- | :--- |
| PAIML-CREW-001 | `apply_guardrails` sets max_iter/max_rpm on a real agent; validators raise on no-evidence real output; `tool_result` prefixes real tool returns |
| PAIML-CREW-002 | Real tools return `SUCCESS:`/`ERROR:` prefixes; original content preserved after prefix |
| PAIML-CREW-003 | All 5 agents guarded; dev/review/test tasks use the correct validator; validation errors feed back to the agent for self-correction |
| PAIML-CREW-004 | Phase-end agents/flows respect CREW_MAX_ITER/CREW_MAX_RPM; completes without regressions |
| PAIML-CREW-005 | Integration suite complements the unit suite (unit suite still passes; coverage stance unchanged) |
| PAIML-CREW-006 | README documents how to run the integration suite against Ollama |
| PAIML-CREW-007 | The suite runs inside `docs/packages/crew/` ticket context (regression: crew-validate loads phase-1 tickets) |

## Acceptance Criteria
- [ ] `crew/tests/test_integration_ollama.py` exists with `@pytest.mark.integration` + `@pytest.mark.ollama`
- [ ] Tests skip cleanly (not fail) when Ollama is unreachable
- [ ] A real Ollama call is made and its output runs through the guardrail validators
- [ ] A runtime loop with low `CREW_MAX_ITER` terminates (no infinite loop) and respects the bounds
- [ ] `CREW_MAX_RPM` is not exceeded over a short window
- [ ] crew-implement wiring test asserts 5 agents guarded + correct task validators vs Ollama
- [ ] phase-end battery resolves and executes with `provider="ollama"`
- [ ] Running `pytest crew/tests/test_integration_ollama.py -m integration -v` against local Ollama passes
- [ ] Existing unit tests still pass: `pytest crew/tests/test_guardrails.py crew/tests/test_llm.py -q`
- [ ] README documents the integration run command and Ollama requirement

## Dependencies
- **Blocked By**: PAIML-CREW-001, PAIML-CREW-002, PAIML-CREW-003, PAIML-CREW-004, PAIML-CREW-005, PAIML-CREW-006, PAIML-CREW-007 (all merged in develop)
- **Blocks**: None
