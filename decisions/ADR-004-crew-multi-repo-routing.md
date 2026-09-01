# ADR-004: Crew engine per-ticket repo routing (multi-repo support)

> This is a repo-wide architectural decision record. All ADRs live under
> `docs/decisions/`. The crew's operational docs live under `docs/packages/crew/`.

## Status
Accepted

## Date
2026-09-01

## Context

The monorepo is split across **separate git repositories** (see `AGENTS.md` "REPO
ROUTING"):

| Disk path | Git repo (remote) |
| :--- | :--- |
| repo root `./` (everything except `docs/` and `infrastracture/`) | `pole-ai-ml` |
| `./docs/` | `pole-ai-ml-docs` (git-ignored by `pole-ai-ml`) |
| `./infrastracture/` | `pole-ai-ml-infra` (git-ignored by `pole-ai-ml`) |

The CrewAI implementation engine (`crew/crew_implement.py`) is **single-repo**: its
worktree lifecycle always runs `git worktree add ... <base>` with `cwd=REPO_ROOT`,
where `REPO_ROOT` is the monorepo root (the `pole-ai-ml` repo). Because
`infrastracture/` and `docs/` are untracked/ignored by `pole-ai-ml`, a fresh worktree
of `pole-ai-ml` **does not contain those directories** — the developer agent cannot
edit files that belong to other repos.

The **keycloak** project (`docs/app/keycloak/`) spans all three repos across its 12
tickets. `detect_project()` derives the project from the docs path
(`docs/app/keycloak/...` → `keycloak`), so **all** keycloak tickets share the same
project name even though they edit different repos:

- 001, 002, 003, 004, 007, 012 → `infrastracture/` (incl. all `helm/` charts) →
  `pole-ai-ml-infra`
- 005, 006, 008, 009, 010, 011 → `app/pole_api/` → `pole-ai-ml`
- 012 → also touches `docs/ENV_VARS.md` → `pole-ai-ml-docs`

Repo ownership therefore **cannot be inferred from the ticket's project name**; it must
be declared explicitly on each ticket.

## Decision

Introduce **per-ticket repo routing** in the crew engine:

1. Each `PAIML-*.md` ticket declares an explicit `## Repository` section naming the
   owning logical repo: `pole-ai-ml` (default), `pole-ai-ml-infra`, or `pole-ai-ml-docs`.
2. The crew parses that into a new `Ticket.repo` field and resolves it to an on-disk
   repo root via a `_repo_root(ticket)` helper.
3. Every repo-bound operation in the worktree lifecycle uses the per-ticket repo root
   instead of the single global `REPO_ROOT`:
   - `create_worktree` / `cleanup_worktree` / `sync_branch_with_base`
   - branch creation / deletion
   - the developer agent's working worktree path
4. `gh pr create` already runs with `cwd=worktree`, so the correct remote
   (`pole-ai-ml` vs `pole-ai-ml-infra` vs `pole-ai-ml-docs`) is auto-detected; PRs are
   opened against the **`develop`** branch of the owning repo. The PR body's `Source:`
   path is made informational (absolute) so it does not crash when the ticket docs live
   in a different repo than the worktree.
5. All work merges into the owning repo's `develop`; `develop → main` remains a manual,
   user-owned release. The crew never pushes to `main`.
6. Test-command handling becomes graceful: `PROJECT_TEST_CMD` gains per-owning-repo
   entries, and a project/repo with **no test suite** (e.g. infra Helm/realm changes)
   is skipped with a log line instead of raising `NotImplementedError`.

### Repo routing table

| Logical repo | On-disk root | Remote | Integration branch |
| :--- | :--- | :--- | :--- |
| `pole-ai-ml` (default) | `REPO_ROOT` | `fpalero/pole-ai-ml` | `develop` |
| `pole-ai-ml-infra` | `REPO_ROOT/infrastracture` | `fpalero/pole-ai-ml-infra` | `develop` |
| `pole-ai-ml-docs` | `REPO_ROOT/docs` | `fpalero/pole-ai-ml-docs` | `develop` |

## Alternatives Considered

### Infer repo from `project` name
Rejected: `detect_project()` keys off the docs path, so all keycloak tickets would map
to one repo, mis-routing the app-code and infra tickets.

### Infer repo by parsing file paths out of ticket prose
Rejected: brittle regex over natural-language steps; risks mis-routing and silently
creating misplaced tracked files in the wrong repo.

### Run separate engine invocations per repo (`REPO_ROOT` env override)
Rejected as a primary mechanism: the dependency graph spans repos (e.g. 005←002,
006←003, 007←004), so a sub-batch of one repo fails validation for missing blockers.

## Consequences

- The crew can implement multi-repo phases in a single `run_phase` pass, in parallel,
  with correct per-repo worktrees and PRs.
- Each keycloak (or any future cross-repo) ticket must carry an accurate
  `## Repository` section; the crew defaults to `pole-ai-ml` when absent.
- A single ticket may still not span two repos (012 touches docs AND infra); such cases
  must be split into per-repo tickets or designate a primary repo and reference the rest.
