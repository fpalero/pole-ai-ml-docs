# 07 — The "Meta" Content: Process & Engineering Systems

> How the whole project is planned, tracked, and built by LLM agents —
> documentation-driven development, the crew engine, multi-repo routing, and
> decision records. Grounded in `docs/decisions/`, `packages/crew/`, and
> `docs/diagrams/agents/`.

## Core articles in this theme

| ID | Title | Difficulty | Primary audience |
| :--- | :--- | :--- | :--- |
| G1 | Documentation-Driven Development: PLAN → Tickets → RAG | Any | All |
| G2 | The Crew: LLM Agents Implementing Your Own Tickets | Advanced | Backend + PM |
| G3 | Multi-Repo Architecture Without Monorepo Pain | Intermediate | Backend + PM |
| G4 | Why Your Project Needs ADRs (Decision Records) | Beginner | All |
| G5 | Guardrails for Autonomous Coding Agents | Intermediate | Backend + PM |
| G6 | AI-Generated UI at Feature Scale: Tabs, Sidebars, Modals | Intermediate | Frontend + PM |

## What makes this theme sellable

- **G2 is bleeding-edge**: `team-lead:plan` → `backlog` → `implementation`, the
  LLM provider factory (opencode / ollama / omni_llm), per-ticket repo routing.
  High interest in agentic coding.
- **G1/G4** differentiate from the "tutorial slop" wave: these show durable
  engineering habits, not just code.
- Repository-splitting with routing rules (docs/infra/apps own repos) is the
  kind of hard-won architectural decision teams pay to read about.

## Source docs

- `docs/decisions/README.md`, `ADR-001..004` (CrewAI flows, LLM provider factory, PR review, multi-repo routing)
- `docs/packages/crew/ADR-002-crew-llm-provider-factory.md`
- `docs/diagrams/agents/FLOW.md`
- `docs/DEVELOPEMENT.md` (repo-wide status / routing)

---

## Docs per audience

- [`ml-cv.md`](ml-cv.md) — ML / computer vision engineers
- [`fullstack-backend.md`](fullstack-backend.md) — full-stack / backend engineers
- [`junior-mixed.md`](junior-mixed.md) — mixed beginner → intermediate
- [`tech-entrepreneur.md`](tech-entrepreneur.md) — entrepreneur / technical PM