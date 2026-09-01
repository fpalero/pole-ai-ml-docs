# PAIML-CREW-012: Add OpenRouter provider support to crew LLM

## Summary
To expand LLM routing options and provide a robust cloud fallback beyond local Ollama/OmniRoute and the OpenCode Zen free tier, we need first-class support for OpenRouter (`openrouter`) in the crew engine.

OpenRouter exposes an OpenAI-compatible API at `https://openrouter.ai/api/v1` and supports a wide variety of models (e.g. DeepSeek, Anthropic Claude, OpenAI GPT, Meta Llama). Adding `openrouter` to `crew/llm.py` allows running multi-agent crews seamlessly by configuring `OPENROUTER_API_KEY` and choosing an OpenRouter model slug.

## Repository
`pole-ai-ml` (root — `crew/llm.py`, `crew/crew_implement.py`)

## Files to modify

### 1. `crew/llm.py` — `build_llm()` OpenRouter branch & constants
- Define default constants:
  - `DEFAULT_OPENROUTER_MODEL = "deepseek/deepseek-chat"` (or `auto` / `openai/auto`)
  - `DEFAULT_OPENROUTER_HOST = "https://openrouter.ai/api/v1"`
- Update `ALLOWED_PROVIDERS`:
  ```python
  ALLOWED_PROVIDERS = ("opencode", "ollama", "omni_llm", "unsloth", "openrouter")
  ```
- Add handler for `provider == "openrouter"`:
  - Model resolution: `model or os.environ.get("CREW_MODEL") or os.environ.get("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL)`
  - URL resolution: `base_url or os.environ.get("OPENROUTER_URL", DEFAULT_OPENROUTER_HOST)` with `_v1()` normalization.
  - API key resolution: `os.environ.get("OPENROUTER_API_KEY")` (or error if missing when executing requests; fallback placeholder for hermetic test setup).
  - Prefix model with `openai/` so litellm routes through the OpenAI-compatible endpoint.
  - Apply `max_retries` (`CREW_LLM_MAX_RETRIES`, default `5`) and `timeout` (`CREW_LLM_TIMEOUT`, default `120`) to handle transient rate limits.
  - Return `(llm, llm)`.
- Update module docstring to document `openrouter` and its environment variables (`OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `OPENROUTER_URL`).

### 2. `crew/crew_implement.py` — CLI help & docstring
- Update CLI argument `--provider` help string to include `openrouter`:
  ```python
  parser.add_argument("--provider", default=os.environ.get("CREW_LLM_PROVIDER", "opencode"),
                      help="LLM provider: opencode, ollama, omni_llm, unsloth, or openrouter")
  ```
- Update `make_llm()` docstring to list `openrouter`.

### 3. Tests — `crew/tests/test_llm.py`
Add unit tests for `openrouter` provider:
- `test_openrouter_returns_crewai_llm`: returns non-null identical instances for flash and pro tiers.
- `test_openrouter_default_model`: model prefixed with `openai/` and matches default.
- `test_openrouter_default_host_uses_v1_endpoint`: base_url points to `https://openrouter.ai/api/v1`.
- `test_openrouter_custom_model_via_env`: `OPENROUTER_MODEL` and `CREW_MODEL` override default.
- `test_openrouter_custom_host_via_env`: `OPENROUTER_URL` env override with `/v1` suffix.
- `test_openrouter_api_key_from_env`: `OPENROUTER_API_KEY` propagates to LLM.
- `test_openrouter_max_retries_and_timeout`: verify default `max_retries=5` and `timeout=120` plus env overrides.

## Acceptance criteria
1. `ALLOWED_PROVIDERS` in `crew/llm.py` includes `"openrouter"`.
2. `build_llm(provider="openrouter")` constructs and returns `(llm, llm)` configured with `model=f"openai/{resolved_model}"`, `base_url="https://openrouter.ai/api/v1"`, `api_key` from `OPENROUTER_API_KEY`, `max_retries`, and `timeout`.
3. `OPENROUTER_MODEL` and `CREW_MODEL` environment variables override the default model.
4. CLI help in `crew/crew_implement.py` lists `openrouter` among valid providers.
5. Unit tests added to `crew/tests/test_llm.py` covering openrouter provider defaults, env overrides, and rate-limit parameters.
6. `pixi run test` passes (all crew tests green, no regressions).

## Dependency graph
- **Blocked By:** PAIML-CREW-011 (rate-limit tuning for LLM gateway)
- **Blocks:** PAIML-KEYCLOAK-001..004 (Keycloak phase 1 crew runs with cloud LLM provider fallback)
