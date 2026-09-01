# Ticket: PAIML-CREW-009

## Repository
pole-ai-ml

## Title
Multi-repo support: per-ticket repo routing for the crew engine

## Description
The crew engine (`crew/crew_implement.py`) is single-repo: its worktree lifecycle
always creates worktrees in the monorepo root (`pole-ai-ml`) via `REPO_ROOT`. The
monorepo is actually split across three git repos (`pole-ai-ml`, `pole-ai-ml-infra`
at `infrastracture/`, `pole-ai-ml-docs` at `docs/`), and `infrastracture/` + `docs/`
are git-ignored by `pole-ai-ml` — so a fresh worktree of `pole-ai-ml` does not contain
those directories and the developer agent cannot edit files belonging to other repos.

The `keycloak` project (`docs/app/keycloak/`, 12 tickets) spans all three repos, but
`detect_project()` derives `keycloak` for every ticket from the docs path, so repo
ownership cannot be inferred from the project name. This ticket makes repo ownership
explicit per ticket (a `## Repository` section) and routes the worktree lifecycle to
the owning repo.

See `docs/decisions/ADR-004-crew-multi-repo-routing.md` for the full decision.

## What to Do

1. **`Ticket` dataclass** (`crew/crew_implement.py`): add `repo: str = "pole-ai-ml"`.
   Parse an explicit `## Repository` section from each `PAIML-*.md`
   (`parse_ticket`); accept `pole-ai-ml`, `pole-ai-ml-infra`, `pole-ai-ml-docs`;
   default to `pole-ai-ml` when absent.
2. **`_repo_root(ticket) -> Path`**: map logical repo → on-disk root:
   - `pole-ai-ml-infra` → `REPO_ROOT / "infrastracture"`
   - `pole-ai-ml-docs` → `REPO_ROOT / "docs"`
   - else → `REPO_ROOT`
3. **Worktree lifecycle uses `_repo_root(ticket)`**: `create_worktree`,
   `cleanup_worktree`, branch creation and deletion, `sync_branch_with_base`, and the
   developer agent's worktree path in `implement_ticket` / `build_crews`. The base
   branch remains `develop` (per repo).
4. **`open_pr`**: keep `cwd=worktree` (the owning repo's remote is auto-detected by
   `gh pr create`). Make the PR body `Source:` path informational — do not call
   `ticket.path.relative_to(REPO_ROOT)` when the ticket docs live in a different repo
   than the worktree (the ticket path belongs to the docs repo).
5. **Graceful test handling**: `run_project_tests`/equivalent must log
   `no test command for project X; skipping` and return a non-failing result instead of
   raising `NotImplementedError` when a repo/project has no test command. Ensures
   infra Helm/realm tickets (which have no pytest suite) do not abort.
6. **Unit tests** in `crew/tests/`: repo parsing (including default), `_repo_root`
   mapping for all three repos, worktree path resolution per repo, and graceful skip
   on a missing test command.

## Acceptance Criteria

- A ticket with `## Repository: pole-ai-ml-infra` creates its worktree inside
  `infrastracture/` (the infra repo) and its PR opens against `pole-ai-ml-infra`
  `develop`.
- A ticket missing `## Repository` defaults to `pole-ai-ml` (backward compatible; all
  existing single-repo tickets unaffected).
- A repo with no test command does not abort the ticket; it logs a skip.
- All PRs target the owning repo's `develop`; never `main`.
- `pixi run crew-validate <any-phase-folder>` still passes; crew unit tests pass with
  ≥80% coverage on the new module.

## Integration Tests to Run (Local Verification)

- Run `pixi run python -m crew docs/app/keycloak --provider ollama` (after the
  keycloak tickets carry a `## Repository` section) and confirm:
  - infra tickets (001-004, 007) open PRs against `pole-ai-ml-infra` `develop`;
  - app tickets (005, 006, 008-011) open PRs against `pole-ai-ml` `develop`;
  - Helm/realm-only tickets do not fail the test step.

## Dependencies

- **Blocks:** None
- **Blocked By:** None

## Estimated Effort

- [M] (Medium ~ 2-4h)
