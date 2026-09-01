# PLAN_PHASE_2 — crew: multi-repo support (per-ticket repo routing)

> Companion detail for `docs/packages/crew/PLAN.md`. Phase 2 adds per-ticket repo
> routing so the crew can implement phases whose tickets span multiple git repos
> (e.g. the `keycloak` project across `pole-ai-ml`, `pole-ai-ml-infra`,
> `pole-ai-ml-docs`). ADR: `docs/decisions/ADR-004-crew-multi-repo-routing.md`.

## Scope

Modify `crew/crew_implement.py` (and supporting tests) so the engine resolves each
ticket to an **owning repo root** instead of a single global `REPO_ROOT`.

## Tasks

- **T2.1** `Ticket` dataclass: add `repo: str = "pole-ai-ml"` field, parsed from an
  explicit `## Repository` section in each `PAIML-*.md` (values: `pole-ai-ml`,
  `pole-ai-ml-infra`, `pole-ai-ml-docs`).
- **T2.2** Add `_repo_root(ticket) -> Path` mapping logical repo → on-disk root:
  `pole-ai-ml-infra` → `REPO_ROOT/infrastracture`, `pole-ai-ml-docs` → `REPO_ROOT/docs`,
  else `REPO_ROOT`.
- **T2.3** Refactor the worktree lifecycle to use `_repo_root(ticket)`:
  `create_worktree`, `cleanup_worktree`, branch creation/deletion, and the developer
  agent's worktree path in `implement_ticket` / `build_crews`.
- **T2.4** `open_pr`: keep `cwd=worktree` (auto-detects the owning repo remote); make
  the PR body `Source:` path informational (don't `relative_to(REPO_ROOT)` when the
  ticket docs live in a different repo).
- **T2.5** Graceful test handling: a repo/project with no test suite logs
  `no test command for project X; skipping` instead of raising `NotImplementedError`.
  Register test commands per owning repo; infra Helm/realm changes skip tests.
- **T2.6** Unit tests in `crew/tests/`: repo parsing, `_repo_root` mapping, worktree
  path resolution per repo, graceful-skip on missing test command.

## Acceptance Criteria

- A ticket with `## Repository: pole-ai-ml-infra` creates its worktree inside
  `infrastracture/` (the infra repo) and its PR opens against `pole-ai-ml-infra`
  `develop`.
- A ticket missing `## Repository` defaults to `pole-ai-ml` (backward compatible).
- A repo with no test command does not abort the ticket; it logs a skip.
- All PRs target the owning repo's `develop`; never `main`.
- Existing single-repo flows (pole_api, pole_ml, pole_analyst, pole_fe) are unchanged.
- `pixi run crew-validate <any-phase-folder>` still passes; unit tests ≥80% coverage.

## Dependencies

- `Blocked By: None` (independent of phase 1; phase 1 may still be in flight).
- `Blocks: None`.
- Runtime prerequisite (not a code blocker): the keycloak tickets gain a `## Repository`
  section so the phase can route correctly.

## Integration / Verification

- Manual: run `pixi run python -m crew docs/app/keycloak --provider ollama` after the
  change and confirm infra tickets open PRs against `pole-ai-ml-infra` and app tickets
  against `pole-ai-ml`, all to `develop`.
