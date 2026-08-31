# ADR-001: CrewAI implementation + phase-end flows with develop-branch + doc/developer wake

## Status
Accepted

## Date
2026-08-30

## Context

We need a workflow where the opencode **team-lead orchestrates** a **CrewAI engine**
(not opencode subagents) to implement tickets. Decided requirements:

- crewAI has the **same behavior** as the opencode subagents (Developer, Reviewer,
  Tester, doc) but is a **separate engine** that does **not interact with opencode**.
- The **team-lead calls the crew** for a phase; the crew **owns the polling** and only
  **updates documentation + the ticket status board** (`.opencode/state/tickets-status.jsonl`)
  so the team-lead stays aware. "When all is green the team-lead is aware; any error is
  documented and readable."
- crew uses the model **`opencode/big-pickle`**.
- Two flows:
  1. **Implementation flow** (`crew-implement`): implementation + pre-PR acceptance QA,
     then opens PRs against **`develop`** and **polls for the merge** itself. On merge
     success it wakes a **doc**-equivalent to document code/package changes + the
     `docs/` relation (manuals, diagrams/classes) and refresh the RAG; on error it wakes
     a **developer**-equivalent to fix.
  2. **Phase-end flow** (`crew-phase-end`, separate script, called manually by the
     team-lead or user when the phase is done): runs the phase integration battery on the
     staging environment **`ipsf-server`** against a **`*_test`** database (never the
     direct/production database), capped at 3 iterations. Report GREEN / ERRORS.

Key constraints preserved from the existing workflow:
- Every feature works in an isolated **`git worktree`** on a **feature branch**.
- The base for every feature branch and PR is **`develop`**, never `main`.
- `develop -> main` is a **manual, user-owned** release performed only after the
  phase-end QA gate is GREEN and the user's own manual testing.
- Token-efficient **pointer-not-payload**: crew reads the ticket file path + runs narrow
  `docs-rag-read` queries; it never receives pasted ticket bodies or doc dumps.

## Decision

Refactor the existing `crew/crew_implement.py` engine and add a phase-end gate so that:

1. **`crew-implement`** (implementation flow):
   - Parses tickets, validates the dependency graph (`validate_dependencies`),
     implements **in parallel** over the ready set.
   - Runs the Developer / Reviewer / Tester crews (now including **doc** and
     **developer-fix** roles) per ticket in an isolated worktree.
   - **Pre-PR acceptance QA** (code conformance + FE-design conformance + fast targeted
     tests) is enforced before a PR opens; capped iterations, then escalate.
   - Feature branches and PRs are based on **`develop`**.
   - After opening the PR, the engine **polls for the merge** itself:
     - merge success + CI green -> delegates a **doc** crew task (document the code /
       package changes and the `docs/` relation: manuals, diagrams/classes) and runs the
       **incremental docs-RAG refresh** (`pixi run docs-rag-write`) + verify; commits the
       RAG manifest.
     - error / BLOCKED / CI red -> delegates a **developer-fix** crew task, then re-runs
       the PR lifecycle.
   - Writes every transition to `.opencode/state/tickets-status.jsonl` and the ticket
     documentation (the single source of truth the team-lead reads).

2. **`crew-phase-end`** (phase-end flow, NEW, separate):
   - Called manually by the team-lead or user once the phase is done.
   - Runs the phase integration battery on the **staging** env (`ipsf-server`) against a
     `*_test` database.
   - Cap 3 iterations: on ERRORS returns the error list and re-runs the failed subset;
     on GREEN reports success.
   - Writes the result to the ticket status board + docs so the team-lead is aware.

## Alternatives Considered

### Polling / wake handled inside opencode (team-lead `gh` loop + Task tool)
- Pros: reuses the existing github-events + ticket-board wake pattern.
- Cons: couples crew progress to an opencode session being open; user explicitly chose
  "crew does not interact with opencode; polling lives with the crew."
- Rejected in favor of crew-owned polling.

### crewAI does the full git lifecycle including `/oc review` + cleanup
- Pros: most autonomous.
- Cons: the existing `/oc review` retry logic is fragile (~40% failure) and duplicates
  the git responsibility. The user selected **Option A**: crew does implementation +
  pre-PR acceptance QA; the crew-reported merge/status is what the team-lead consumes.
- Adopted: crew polls for merge but the source of truth is the documented status, not an
  opencode subagent call.

## Consequences

- The opencode team-lead's role for a phase is: call `crew-implement`, then watch the
  ticket board / docs; call `crew-phase-end` manually when the phase is done.
- `crew/` now owns a `doc`-equivalent (markdown + RAG sync) and a `developer-fix`
  recovery role, so it must have `pixi`/`gh`/git on `$PATH` and access to the docs RAG
  scripts.
- The model for all crew agents is `opencode/big-pickle` unless overridden.
- Anything the crew changes must stay on `develop`; the user promotes `develop -> main`.
