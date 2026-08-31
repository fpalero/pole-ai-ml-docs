# ADR-002: Crew engine LLM provider factory (opencode / ollama / omni_llm)

> This is a repo-wide architectural decision record. All ADRs live under
> `docs/decisions/` (see `docs/decisions/ADR-001-crewai-implementation-flows.md`).
> The crew's operational docs live under `docs/packages/crew/`.

## Status
Accepted

## Date
2026-08-31

## Context

The crew engine (`crew/`) runs CrewAI agents (Developer, Reviewer, Tester, doc,
developer-fix) that need an OpenAI-compatible LLM endpoint. Originally the engine
hardcoded the opencode gateway (`opencode/big-pickle` via `OPENCODE_URL`) as the
single way to reach a model. As the team works across different environments, we
need to run the same engine against different model backends without editing code:

- **Local development** may want a fully local model (Ollama) to avoid paying for /
  depending on a remote gateway.
- **Higher-throughput or fallback scenarios** may want a routed gateway (OmniRoute)
  with a key supplied at runtime.
- The existing opencode gateway must remain the **default** so nothing breaks.

The key provider, OmniRoute, authenticates with an API key. That key is a **secret**
and must never be committed to the repo.

## Decision

Introduce a provider factory, `build_llm()` in `crew/llm.py`, that returns a CrewAI
`LLM` instance for one of three OpenAI-compatible providers, selected by a
`--provider` flag (on both `crew-implement` and `crew-phase-end`) or the
`CREW_LLM_PROVIDER` env var (default `opencode`):

| Provider | Endpoint | Default model | Key handling |
| :--- | :--- | :--- | :--- |
| `opencode` | `OPENCODE_URL` | `opencode/big-pickle` | `OPENCODE_API_KEY` / `local` |
| `ollama` | Ollama `/v1` (`OLLAMA_HOST`) | `qwen3.8:27b` | none (local) |
| `omni_llm` | OmniRoute `/v1` (`OMNIROUTE_URL`) | `auto` | `OMNIROUTE_API_KEY` env var |

The `--provider` value is threaded through `run_phase` → `implement_ticket` →
`make_llm` → `build_llm` (and the equivalent phase-end path) so every agent and
task uses the same selected provider.

The OmniRoute API key is read **only** from the `OMNIROUTE_API_KEY` environment
variable at runtime. It is not stored in any file in the repo; the `.env.example`
documents the variable name but carries no value, and `crew/README.md` instructs
users to export it in their shell before running.

## Alternatives Considered

### Hardcode the opencode gateway as the only option
- Pros: simplest, no new configuration surface, matches the original single-backend
  behavior.
- Cons: forces every environment to use the opencode gateway; no path to a fully
  local (Ollama) run or a routed gateway without code changes; couples the engine to
  one provider's availability/contract.
- Rejected: the team needs the same engine across local and routed backends, so the
  factory must be configurable at runtime.

### A single configurable base URL + model pair (no named providers)
- Pros: minimal code, one knob.
- Cons: every backend has slightly different auth and routing (Ollama needs the
  `openai/` model prefix for litellm; OmniRoute needs a required key; opencode has
  flash/pro tiers), so a single generic pair cannot express the per-provider defaults
  and key handling cleanly.
- Rejected: named providers let each backend encode its own endpoint, default model,
  and key semantics while keeping a uniform `--provider` interface.

### Commit the OmniRoute API key (e.g. in `.env` / a config file)
- Pros: zero-config for anyone with access to the repo.
- Cons: leaks a live credential into version history; any future rotation or exposure
  is irreversible; violates the repo's secret-handling policy.
- Rejected: the key is read from the `OMNIROUTE_API_KEY` env var only, and never
  committed.

## Consequences

- The crew engine is now provider-agnostic: the same tickets, PRs, and phase-end gate
  run against opencode, a local Ollama, or OmniRoute by changing one flag/env var.
- `opencode` remains the default, so existing behavior is unchanged unless a provider
  is explicitly selected.
- OmniRoute users must export `OMNIROUTE_API_KEY` before running; this is documented
  in `crew/README.md` and `.env.example`. No secrets are introduced into the repo.
- The factory is covered by 30 focused unit tests (`crew/tests/test_llm.py`, `llm`
  marker) so each provider's endpoint, model, and key handling are pinned down.
- Env-var contracts (`OPENCODE_*`, `OLLAMA_*`, `OMNIROUTE_*`) become part of the
  engine's public surface and should be maintained in `crew/README.md` as providers
  evolve.
