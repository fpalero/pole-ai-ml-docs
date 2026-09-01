# PAIML-CREW-011: Rate-limit tuning for the OpenCode Zen gateway (retries, timeout, RPM)

## Summary
Running the phase-1 Keycloak crew with the OpenCode provider (`big-pickle` via
`https://opencode.ai/zen/v1`) fails immediately with:

```
litellm.RateLimitError: OpenAIException - Error from provider (Console):
Rate limit exceeded. Please try again later.
```

The routing fix (PAIML-CREW-010 / PR #169) is verified working end-to-end, but the
crew still overwhelms the free-tier gateway:

- The crew engine launches up to `DEFAULT_MAX_PARALLEL=3` tickets in parallel
  (`ThreadPoolExecutor`), each spawning multi-agent sequential crews.
- Every agent is rate-capped at `CREW_MAX_RPM` default **15** requests/minute —
  far too aggressive for the free tier.
- The `crewai.llm.LLM` is built with **no `max_retries` / `timeout`**, so the first
  transient `429 Rate limit exceeded` kills the task instead of backing off.

This ticket adds durable rate-limit handling so the crew survives the gateway's
free-tier limits: configurable retries/timeout on the LLM and a conservative default
per-agent RPM — plus a serial launch recipe (`--max-parallel 1`) for heavy phases.

## Repository
`pole-ai-ml` (root — `crew/llm.py`, `crew/guardrails.py`)

## Files to modify

### 1. `crew/llm.py` — `build_llm()` opencode branch
Add environment-configurable retries and timeout to the `LLM(...)` construction so a
transient `429` backs off instead of failing the task:

```python
max_retries = int(os.environ.get("CREW_LLM_MAX_RETRIES", "5"))
timeout = int(os.environ.get("CREW_LLM_TIMEOUT", "120"))
llm = LLM(model=f"openai/{bare}", api_key=api_key, base_url=url,
          max_retries=max_retries, timeout=timeout)
```

Also update the module docstring, which still references the stale
`provider="ollama" -> openai/qwen3.8:27b` example, to document the new settings.

### 2. `crew/guardrails.py` — conservative `CREW_MAX_RPM` default
Lower the default per-agent request rate from `15` to `3` requests/minute
(still env-overridable):

```python
CREW_MAX_RPM: int = int(os.environ.get("CREW_MAX_RPM", "3"))
```

Update the module docstring's configuration table to match (`default 3`).

### 3. Tests
- `crew/tests/test_llm.py`: assert the opencode branch LLM carries
  `max_retries`/`timeout` and that `CREW_LLM_MAX_RETRIES` / `CREW_LLM_TIMEOUT` env
  overrides propagate.
- `crew/tests/test_guardrails.py`: assert `CREW_MAX_RPM` default is `3`
  (and is env-overridable).

## Acceptance criteria
1. `build_llm("opencode", ...)` returns an LLM with `max_retries=5`, `timeout=120`
   by default (env-overridable).
2. `apply_guardrails` applies `max_rpm=3` by default (env-overridable).
3. A real CrewAI `Crew.kickoff()` against `https://opencode.ai/zen/v1` survives
   transient rate limits via litellm backoff (no immediate task failure).
4. `pixi run test` passes (all crew tests green, no regressions).

## Dependency graph
- **Blocked By:** PAIML-CREW-010 (opencode routing fix — merged, PR #169)
- **Blocks:** PAIML-KEYCLOAK-001..004 (phase 1 launch reliability on free tier)