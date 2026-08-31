# Flow — Agents (Team-Lead Implementation Workflow)

> How the AI agent team implements a feature end-to-end. High-level command flow plus a low-level
> view of how **team-lead** orchestrates the **developer**, **reviewer** and **tester** agents,
> including commit → review → test → Pull Request.
>
> Roles referenced: **team-lead** (plans + orchestrates), **developer** (implements, TDD, git
> worktree), **reviewer** (code review/QA), **tester** (live validation), **general/explore**
> (research).

---

## 1. High-Level Flow (the commands a user runs)

```mermaid
flowchart TD
    U[User] --> P["team-lead:plan"]
    P -->|reads docs + repo, creates PLAN| B["team-lead_backlog"]
    B -->|breaks plan into tickets / backlog| I["team-lead:implementation"]
    I -->|orchestrates dev + review + test| OUT[Feature shipped: commits + reviewed + tested + PR]

    subgraph ARTIFACTS["Artifacts produced"]
        PLAN["Implementation Plan (PLAN.md)"]
        BACK["Backlog / ticket list (PAIML-...)"]
        PR["Pull Request"]
    end

    P --> PLAN
    B --> BACK
    OUT --> PR
```

**What each step does**

| Step | Command | Description |
| :--- | :--- | :--- |
| **Plan** | `team-lead:plan` | Team-lead reads the project docs (`docs/.../PLAN.md`, specs, tickets) and the current repo, then produces an implementation plan with phases/steps and a DoD. |
| **Backlog** | `team-lead_backlog` | Team-lead converts the plan into a concrete, ordered backlog of tickets (each scoped and sequenced), including dependencies and effort estimates. |
| **Implementation** | `team-lead:implementation` | Team-lead orchestrates the developer/reviewer/tester agents to implement the backlog, then integrate the result (review + test + PR). |

---

## 2. Low-Level Flow (how team-lead orchestrates the work)

### 2.1 Orchestration overview

```mermaid
flowchart TD
    TL["team-lead:implementation"]

    TL -->|dispatch ticket| DEV1["developer A (git worktree)"]
    TL -->|dispatch ticket| DEV2["developer B (git worktree)"]
    TL -->|dispatch ticket| DEV3["developer C (git worktree)"]

    DEV1 -->|implement + TDD + commit| W1["branch / worktree A"]
    DEV2 -->|implement + TDD + commit| W2["branch / worktree B"]
    DEV3 -->|implement + TDD + commit| W3["branch / worktree C"]

    W1 --> RV["reviewer"]
    W2 --> RV
    W3 --> RV
    RV -->|feedback| DEV1
    RV -->|feedback| DEV2
    RV -->|feedback| DEV3

    W1 --> TE["tester (isolated env)"]
    W2 --> TE
    W3 --> TE
    TE -->|results| TL

    RV -->|approved| TL
    TL -->|merge + PR| PR["Pull Request (base ← feature)"]
```

> **Parallelization:** independent tickets run on **separate git worktrees** so multiple developers
> work at the same time without colliding. team-lead dispatches, then aggregates results.

### 2.2 Per-ticket lifecycle (developer → reviewer → tester)

```mermaid
sequenceDiagram
    participant TL as Team-Lead
    participant D as Developer
    participant R as Reviewer
    participant T as Tester
    participant G as Git/GitHub

    TL->>D: dispatch ticket (spec + acceptance criteria)
    loop TDD cycle
        D->>D: write failing test → implement → refactor
    end
    D->>G: commit (concise, matches repo style)
    D-->>TL: ready for review
    TL->>R: review code (bug/arch/security)
    R-->>D: feedback (if needed)
    D->>D: address feedback
    R-->>TL: approved
    TL->>T: validate in isolated env (live run)
    T-->>TL: pass/fail results
    TL->>G: create/update Pull Request (base ← feature)
    TL->>TL: record in backlog (done)
```

---

## 3. Step-by-step Process (prose)

### 3.1 `team-lead:plan`
1. **Gather context** — team-lead reads the relevant docs (e.g. `docs/app/pola_api/PLAN.md`), the
   ticket(s), and the current codebase to understand the goal and constraints.
2. **Produce a plan** — an ordered set of phases/steps with scope, affected components, and a
   Definition of Done, written to a `PLAN.md`-style doc.
3. **Surface questions** — team-lead asks the user for confirmation/decisions before proceeding.

### 3.2 `team-lead_backlog`
1. **Break the plan down** — turn each phase into concrete, atomic tickets (with IDs like
   `PAIML-...`), each with scope, dependencies, and effort.
2. **Order and sequence** — tickets are ordered by dependency so parallel work is safe.
3. **Update tracking** — ticket counter (`PROJECT_VARS.md`) is advanced as tickets are created.

### 3.3 `team-lead:implementation`
1. **Dispatch** — each independent ticket goes to a **developer** running in its own **git
   worktree**; dependent tickets wait for their prerequisites.
2. **Develop (TDD)** — the developer writes a failing test, implements the change, and refactors,
   committing with a concise message matching the repo style. The worktree isolates the change.
3. **Review** — the **reviewer** inspects the branch for bugs, architecture, security, and test
   coverage; feedback loops back to the developer until approved.
4. **Test** — the **tester** runs the change in an isolated test environment (live execution /
   automated validation) and reports pass/fail to team-lead.
5. **Integrate** — approved, passing branches are merged and a **Pull Request** is opened from the
   feature branch to the base branch, summarizing the change.
6. **Track** — completed tickets are marked done in the backlog.

---

## 4. Key Principles

| Principle | Why |
| :--- | :--- |
| **Plan before code** | `plan` → `backlog` → `implementation` keeps work scoped and approved up front. |
| **Git worktree isolation** | Developers edit without conflicting; enables parallel feature work. |
| **TDD** | Failing-test-first guarantees each change is testable and covered. |
| **Independent review** | Reviewer catches bugs/arch/security that the developer may miss. |
| **Live validation** | Tester verifies behavior in an isolated environment, not just by inspection. |
| **Single PR per feature** | Clear, reviewable diff from feature → base. |
