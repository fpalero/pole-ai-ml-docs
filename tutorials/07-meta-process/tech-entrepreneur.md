# Theme 07 — The "Meta" Content: Process & Engineering Systems · Audience: Entrepreneur / Technical PM

> Process that *outputs* software: an agent crew that works your tickets, a
> repo topology you can reason about, and decision records that make a tiny
> team look like a mature org.

## Catalog

### G2 (scaled) — A Software Team That Scales Without Sales Pipeline… The Agent Crew Story ⭐
- **Difficulty:** Advanced
- **Type:** Case study
- **Hook:** "Plan → backlog → PRs, mostly autonomous. The org chart fits on one page."
- **Description:** The crew engine as a startup story: team-lead planning,
  backlog decomposition into scoped tickets, implementer/reviewer/tester agents,
  per-ticket repo routing, and the LLM provider factory. Shows a replicable
  blueprint for a founder running a one-person (or zero-person) engineering team.
- **Grounding:** `docs/decisions/ADR-001..004`, `docs/diagrams/agents/FLOW.md`.
- **Sellable angle:** Distinct product-strategy content — "how to run engineering
  without headcount."

### G3 (scaled) — Repo Topology for a Growing Product
- **Difficulty:** Intermediate
- **Type:** Technical-architecture explainer
- **Hook:** "The day your monorepo stops being one repo is the day you need rules, not courage."
- **Description:** The multi-repo decision from a founder's lens: what to split
  (code / docs / infra), a routing table as the source of truth, and branch
  policies that protect the mainline. High value for PMs overseeing org growth.
- **Grounding:** `docs/decisions/ADR-004-crew-multi-repo-routing.md`.
- **Sellable angle:** Growth-stage architecture narrative.

### G4 (scaled) — Decision Records as People-Onboarding
- **Difficulty:** Beginner
- **Type:** Practice guide
- **Hook:** "Answers to 'why is it like this?' already exist — in the decisions repo."
- **Description:** ADRs positioned as institutional memory: cut onboarding
  time, reduce repeated debates, and (crucially) feed future agents. Includes a
  template.
- **Grounding:** `docs/decisions/README.md`.
- **Sellable angle:** Ops/management value of a developer practice.