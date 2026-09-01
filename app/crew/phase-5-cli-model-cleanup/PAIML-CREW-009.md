# PAIML-CREW-009: Unify model flags — replace --model-flash/--model-pro with --model

## Summary
Replace the two-tier `--model-flash`/`--model-pro` CLI flags with a single `--model`
flag across the crew engine.  Both flash and pro tiers use the same model.  Add
`--model` to `crew_phase_end.py` for parity.  Add an ergonomic `crew` pixi task alias.

## Repository
`pole-ai-ml` (root — `crew/`, `pixi.toml`)

## Files to modify

### 1. `crew/llm.py` — `build_llm()`
- **Before:** `build_llm(provider, model_flash=None, model_pro=None, base_url=None)`
- **After:** `build_llm(provider, model=None, base_url=None)`
- All providers use the same `model` for both tiers.
- Return `(llm, llm)` (same instance).
- Env fallback: `CREW_MODEL` → provider default (e.g. `qwen3.8:27b` for ollama).
- Remove `OPENCODE_MODEL_FLASH` / `OPENCODE_MODEL_PRO` env var lookups.
- Keep `ALLOWED_PROVIDERS`, `_v1()`, provider-specific defaults unchanged.

### 2. `crew/crew_implement.py` — CLI + wiring
- `make_llm(model_flash, model_pro, base_url, provider)` → `make_llm(model, base_url, provider)`
- `implement_ticket(ticket, model_flash, model_pro, ...)` → `implement_ticket(ticket, model, ...)`
- `run_phase(folder, ..., model_flash, model_pro, ...)` → `run_phase(folder, ..., model, ...)`
- `main()` argparse: remove `--model-flash` / `--model-pro`, add `--model`
  - `parser.add_argument("--model", default=os.environ.get("CREW_MODEL"), ...)`
  - Pass `args.model` to `run_phase()`.
- Remove `OPENCODE_MODEL_FLASH` / `OPENCODE_MODEL_PRO` env var references.

### 3. `crew/crew_phase_end.py` — add `--model` flag
- Already has `--provider`. Add `--model`:
  - `parser.add_argument("--model", default=os.environ.get("CREW_MODEL"), ...)`
- Pass `model` to `run_ticket_integration()` (currently unused by integration cmds,
  but available for future CrewAI-agent-based integration batteries).

### 4. `pixi.toml` — add `crew` task alias
- Add: `crew = { cmd = "python -m crew", cwd = "." }`
- Keep existing `crew-implement`, `crew-validate`, `crew-setup`, `crew-phase-end`.

### 5. Tests
- `crew/tests/test_llm.py`: update all `build_llm(model_flash=..., model_pro=...)` → `build_llm(model=...)`
- `crew/tests/test_integration_ollama.py`: update `build_llm` calls
- `crew/tests/test_multi_repo.py`: no changes expected (doesn't touch model args)

## CLI examples after change
```bash
# Ollama (defaults to qwen3.8:27b @ localhost:11434)
pixi run crew --provider ollama docs/app/keycloak/phase-1-keycloak-realm-theme/

# Ollama with explicit model
pixi run crew --provider ollama --model qwen3.8:27b docs/app/keycloak/phase-1-keycloak-realm-theme/

# Opencode (defaults to opencode/big-pickle)
pixi run crew --provider opencode --url https://opencode.ai/zen/v1 docs/app/keycloak/phase-1-keycloak-realm-theme/

# Phase-end gate
pixi run crew-phase-end --provider ollama docs/app/keycloak/phase-1-keycloak-realm-theme/
```

## Acceptance criteria
1. `pixi run crew --provider ollama docs/app/keycloak/phase-1-keycloak-realm-theme/` works end-to-end.
2. `pixi run crew-phase-end --provider ollama docs/app/keycloak/phase-1-keycloak-realm-theme/` accepts `--model`.
3. `pixi run crew-validate docs/app/keycloak/` still passes (no model args needed).
4. `pixi run test` passes (all crew tests green).
5. No references to `model_flash`, `model_pro`, `OPENCODE_MODEL_FLASH`, `OPENCODE_MODEL_PRO` remain in crew code.

## Dependency graph
- **Blocked By:** none
- **Blocks:** PAIML-KEYCLOAK-001..004 (phase 1 launch depends on working ollama CLI)
