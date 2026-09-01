# PAIML-CREW-010: Fix opencode provider LLM model routing (openai/ prefix)

## Summary
The crew engine's `--provider opencode` LLM fails with
`litellm.BadRequestError: LLM Provider NOT provided ... model=opencode/big-pickle`
because litellm does not recognize `opencode/` as a provider prefix and the OpenCode
Zen gateway rejects the literal `opencode/big-pickle` model id.

The fix makes the `opencode` provider use the same `openai/<model>` prefix + `base_url`
pattern as the `ollama`/`omni_llm`/`unsloth` branches. litellm then routes via the
`openai` provider, strips the `openai/` prefix, and sends the bare model id
(`big-pickle`) to the configured base URL.

## Repository
`pole-ai-ml` (root — `crew/llm.py`)

## Files to modify

### 1. `crew/llm.py` — `build_llm()` opencode branch
- **Before:**
  ```python
  llm = LLM(model=resolved_model, api_key=api_key, base_url=url)
  ```
  where `resolved_model` defaults to `opencode/big-pickle`.
- **After:**
  ```python
  llm = LLM(model=f"openai/{resolved_model}", api_key=api_key, base_url=url)
  ```
  where `resolved_model` stays `opencode/big-pickle` by default but is now sent as
  `openai/opencode/big-pickle`? **No** — see note below.

### Model string caveat (verified empirically)
- `model="opencode/big-pickle"` → litellm `Provider NOT provided` (no route).
- `model="openai_like/big-pickle"` → litellm `Unmapped LLM provider openai_like`.
- `model="openai/big-pickle"` + `base_url=https://opencode.ai/zen/v1` → routes correctly,
  sends `big-pickle` to the gateway (only hits a transient gateway rate limit).
- `model="openai/big-pickle"` must therefore be produced by **replacing** the `opencode/`
  prefix, i.e. strip the `opencode/` slug then prefix with `openai/`:
  ```python
  # the opencode gateway model id is "big-pickle"; strip any "opencode/" prefix
  bare = resolved_model.removeprefix("opencode/")
  llm = LLM(model=f"openai/{bare}", api_key=api_key, base_url=url)
  ```
  This sends `big-pickle` (not `opencode/big-pickle`) to the gateway.

### 2. Tests
- `crew/tests/test_llm.py`: add/extend a case asserting the opencode branch produces
  `LLM.model == "openai/big-pickle"` (and base_url passthrough).

## Acceptance criteria
1. `build_llm("opencode", model="opencode/big-pickle")` returns
   `LLM(model="openai/big-pickle", base_url=<url>, api_key=<key>)`.
2. A real CrewAI `Crew.kickoff()` with the opencode LLM reaches the gateway and gets a
   completion (subject to gateway rate limits) — no `Provider NOT provided` / `not supported`.
3. `pixi run test` passes (all crew tests green).
4. `pixi run crew --provider opencode --url https://opencode.ai/zen/v1 docs/app/keycloak/phase-1-keycloak-realm-theme/`
   no longer fails with the provider/model routing error.

## Dependency graph
- **Blocked By:** none
- **Blocks:** PAIML-KEYCLOAK-001..004 (phase 1 launch depends on a working opencode LLM)
