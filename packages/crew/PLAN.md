# Implementation Plan — crew (CrewAI Implementation Engine)

> CrewAI-based multi-agent engine that implements opencode tickets end-to-end.
> Lives at `crew/` (top-level dev-tooling package, not part of the runtime product).

## Phase Table

| Phase | Name | Tickets | Status |
| :--- | :--- | :--- | :--- |
| 1 | Guardrails (anti-infinite-loop) | `PAIML-CREW-001..008` | 🟡 PARTIAL (código implementado en `develop`; falta `PAIML-CREW-008` integración + Ollama) |
| 2 | Multi-repo support (per-ticket repo routing) | `PAIML-CREW-009` | 📋 PLANNED |

---

## Phase Details

### Phase 2 — Multi-repo support (per-ticket repo routing)

**Goal:** Let the crew implement phases whose tickets span multiple git repos (e.g. the
`keycloak` project across `pole-ai-ml`, `pole-ai-ml-infra`, `pole-ai-ml-docs`). Each
ticket declares an explicit `## Repository` section; the worktree lifecycle routes to
the owning repo. See `docs/decisions/ADR-004-crew-multi-repo-routing.md`.

**Tickets:**

| Ticket | Title | Summary |
| :--- | :--- | :--- |
| `PAIML-CREW-009` | Multi-repo support | Add `Ticket.repo` + `## Repository` parsing, `_repo_root()` mapping, per-repo worktree lifecycle + PR target, graceful skip when a repo has no test command |

**Dependencies:**
- `PAIML-CREW-009` `Blocked By: None`; independent of phase 1.
- Runtime prerequisite (not a code blocker): keycloak tickets gain a `## Repository`
  section so the phase routes correctly.

**Acceptance Criteria:**
- `pole-ai-ml-infra` tickets create worktrees inside `infrastracture/` and open PRs
  against `pole-ai-ml-infra` `develop`; `pole-ai-ml`/`pole-ai-ml-docs` route likewise.
- Tickets missing `## Repository` default to `pole-ai-ml` (backward compatible).
- A repo with no test command logs a skip rather than aborting the ticket.
- All PRs target the owning repo's `develop`; never `main`.
- Crew unit tests ≥80% coverage on the new module; `pixi run crew-validate` still passes.

---

## Phase Details

### Phase 1 — Guardrails (anti-infinite-loop)

**Goal:** Prevent CrewAI agents from getting trapped in infinite loops caused by repetitive
tool calls, vague tool feedback, or "loop drift". Implement structural and algorithmic
guardrails using native CrewAI configuration parameters, task validation, and explicit
tool success states.

**Scope:**
- `crew/guardrails.py` — new module with agent wrapper, task validators, tool helpers
- `crew/crew_implement.py` — apply guardrails to all 5 agents + refactor tools
- `crew/crew_phase_end.py` — apply guardrails to phase-end workflow
- `crew/tests/test_guardrails.py` — unit tests
- `crew/tests/test_integration_ollama.py` — integration tests against local Ollama
- `crew/README.md` — document new env vars + integration run command

**Tickets:**

| Ticket | Title | Summary |
| :--- | :--- | :--- |
| `PAIML-CREW-001` | Guardrails module | Create `crew/guardrails.py` with `apply_guardrails()`, task validators, and `tool_result()` helper |
| `PAIML-CREW-002` | Tool refactor (SUCCESS/ERROR) | Refactor all tools in `crew_implement.py` to return explicit `SUCCESS:` / `ERROR:` prefixed messages |
| `PAIML-CREW-003` | Apply guardrails to agents + tasks | Wire `apply_guardrails()` on all 5 agents; add `guardrail=` to dev/review/test tasks |
| `PAIML-CREW-004` | Phase-end guardrails | Apply the same guardrails to `crew/crew_phase_end.py` workflow |
| `PAIML-CREW-005` | Unit tests | Unit tests for guardrail functions, tool result formatting, and validator logic |
| `PAIML-CREW-006` | Documentation update | Update `crew/README.md` with new env vars (`CREW_MAX_ITER`, `CREW_MAX_RPM`) and guardrail behavior |
| `PAIML-CREW-007` | Fix `detect_project` for `docs/packages/` | Make `detect_project()` recognize the plural `packages` segment so package tickets load (prerequisite) |
| `PAIML-CREW-008` | Integration tests (guardrails + Ollama) | New `crew/tests/test_integration_ollama.py` exercising guardrails against local Ollama (`qwen3.8:27b`); covers all phase-1 runtime acceptance criteria |

**Dependencies:**
- `PAIML-CREW-007` (fix `detect_project`) is a prerequisite so package tickets load at all. The remaining tickets have no external blockers.
- `PAIML-CREW-008` (integration tests) depends on `PAIML-CREW-001..007` being merged in `develop` and on local Ollama (`qwen3.8:27b`) being reachable.

**Acceptance Criteria:**
- All 5 agents have `max_iter` and `max_rpm` set via env vars
- All tools return deterministic `SUCCESS:` / `ERROR:` prefixed messages
- Task guardrail validators catch missing class definitions, missing verdicts, etc.
- Guardrails module works in both `crew-implement` and `crew-phase-end` flows
- `detect_project()` recognizes `docs/packages/` so crew can operate on its own + package docs
- Unit tests pass with ≥80% coverage on the new module
- README documents all new env vars with defaults and examples
- Integration tests (`crew/tests/test_integration_ollama.py`, marker `integration`/`ollama`) pass against local Ollama and skip cleanly when Ollama is offline
