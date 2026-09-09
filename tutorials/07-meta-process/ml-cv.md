# Theme 07 — The "Meta" Content: Process & Engineering Systems · Audience: ML / CV Engineers

> For engineers who also own their process: docs-driven development, ADRs, and
> even having LLM agents implement tickets. You already do the engineering;
> this makes the workflow repeatable.

## Catalog

### G1 — Documentation-Driven Development: PLAN → Tickets → RAG
- **Difficulty:** Any
- **Type:** Workflow guide
- **Hook:** "The docs aren't a report you write after the code — they're the steering wheel."
- **Description:** The full loop: `PLAN.md` + per-phase plan files → decomposed
  tickets with acceptance criteria + effort → implementation → docs RAG
  retrieval. Shows how every feature stays traceable and re-queryable.
- **Grounding:** `docs/diagrams/agents/FLOW.md`, `docs/DEVELOPEMENT.md`.
- **Sellable angle:** Differentiates from code-only tutorials; high value for
  engineering-lead ML devs.

### G4 — Why Your Project Needs ADRs (Decision Records)
- **Difficulty:** Beginner
- **Type:** Practice guide
- **Hook:** "Six months from now, will you remember *why* you chose that architecture?"
- **Description:** The ADR discipline via a real set (provider factory, PR
  review workflow, multi-repo routing): what to record, at what depth, and how
  a decisions tree becomes onboarding material for teammates and agents alike.
- **Grounding:** `docs/decisions/README.md`, `ADR-001..004`.
- **Sellable angle:** Cheap to produce, evergreen, and professional.