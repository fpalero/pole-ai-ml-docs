# Theme 07 — The "Meta" Content: Process & Engineering Systems · Audience: Full-Stack / Backend Engineers

> Process-as-engineering: the crew engine that implements tickets, multi-repo
> routing that keeps repos sane, and the ADR discipline that makes it all
> legible.

## Catalog

### G2 — The Crew: LLM Agents Implementing Your Own Tickets
- **Difficulty:** Advanced
- **Type:** Systems guide
- **Hook:** "Your plan becomes a backlog, your backlog becomes PRs — and an agent crew drives it."
- **Description:** The `crew` engine end to end: `team-lead:plan` →
  `team-lead:backlog` → `team-lead:implementation` orchestrating
  developer/reviewer/tester agents, the LLM provider factory (opencode / ollama
  / omni_llm), ticket lifecycle state (`tickets-status.jsonl`), full-patch review
  gate, and per-ticket repo routing.
- **Grounding:** `docs/decisions/ADR-001-crewai-implementation-flows.md`, `docs/packages/crew/ADR-002-crew-llm-provider-factory.md`, `docs/decisions/ADR-004-crew-multi-repo-routing.md`.
- **Sellable angle:** Bleeding-edge agentic content with a real implementation.

### G3 — Multi-Repo Architecture Without Monorepo Pain
- **Difficulty:** Intermediate
- **Type:** Architecture guide
- **Hook:** "Code, infra, and docs in separate repos — with rules that keep it from becoming chaos."
- **Description:** The repo-splitting pattern: one repo per concern (code / docs
  / infra), absolute path→repo routing table, worktree-based feature branches,
  and the branch policies (develop integration, main user-owned release). For
  mid-size teams deciding between mono and multi.
- **Grounding:** `docs/decisions/ADR-004-crew-multi-repo-routing.md`, `docs/DEVELOPEMENT.md`.
- **Sellable angle:** Decision-grade architecture content.

### G1 (adapted) — Running a Docs-Driven Backend Project
- **Difficulty:** Any
- **Type:** Workflow guide
- **Hook:** "An HTTP API reference that regenerates from /openapi.json — plus hand-maintained conventions."
- **Description:** The backend spin on doc-driven dev: generated endpoint
  references vs hand-maintained cross-cutting conventions, ticket naming
  (PAIML-<PROJECT>-NNN), and phase plans that gate releases.
- **Grounding:** `docs/app/pole_api/API.intro.md`, `docs/app/pole_api/POLE-API.md`.
- **Sellable angle:** Practical conventions backend leads will lift directly.

### G5 — Guardrails for Autonomous Coding Agents
- **Difficulty:** Intermediate
- **Type:** Safety/systems guide
- **Hook:** "Let the agents code — but give them rails that make the risk boring."
- **Description:** The safety layer around an agent crew: small-step ticket
  lifespan, bounded/defined agent roles, guardrail checks on behavior
  (off-script catches), review/test gates before merge, and ADRs recording the
  why. What makes unsupervised-generation viable in a real repo.
- **Grounding:** `docs/packages/crew/PLAN.md`, `docs/packages/crew/phase-1-guardrails/PAIML-CREW-001/005.md`.
- **Sellable angle:** Safety-of-agentic-coding content is high-demand and thin
  on real implementations.

### G6 — AI-Generated UI at Feature Scale: Tabs, Sidebars, Modals
- **Difficulty:** Intermediate
- **Type:** Frontend/product engineering guide
- **Hook:** "AI can generate one screen. Keeping 40 coherent screens under control is the real skill."
- **Description:** When AI generates the frontend, orchestration is the hard
  part: phase-by-phase shell, tab/sidebar navigation and history, detail
  modals, upload-progress panels, results views, and parity between generated
  screens. The `pole_analyst` playbook for feature-scale AI-generated UI.
- **Grounding:** `docs/app/pole_analyst/PLAN.md` + phase plans,
  `docs/diagrams/pole_analyst/FLOW.md`, `docs/app/pole_analyst/fe_design.md`.
- **Sellable angle:** The scaling companion to the single-screen AI-UI
  tutorials everyone writes; proves methodology at product scale.