# Architecture Decision Records (ADR)

This is the **canonical, repo-wide home for Architecture Decision Records (ADRs)**.

Every ADR captures the *why* behind a significant architectural decision: context,
the decision, and its consequences — so future engineers and agents can understand
the codebase.

## Convention

- **Location:** `docs/decisions/ADR-<NNN>-<kebab-slug>.md`
- **Numbering:** sequential (`ADR-001`, `ADR-002`, …). Pick the next free number.
- **Format:** use the MADR (Markdown Any Decision Record) style — `Status` / `Date` /
  `Context` / `Decision` / `Consequences` (see the existing ADRs in this folder).

## Rule (git)

`docs/decisions/` is **tracked** in the `pole-ai-ml` repo. The root `.gitignore`
un-ignores it:

```
docs/*
!docs/decisions/
!docs/decisions/**
```

So new ADRs placed here are committed automatically. ADRs are **not** project-scoped
to `docs/app/<project>/` or `docs/packages/<project>/` — they cover decisions that may
span the whole repo.

## Existing ADRs

- `ADR-001-crewai-implementation-flows.md` — CrewAI implementation + phase-end flows.
- `ADR-002-crew-llm-provider-factory.md` — Crew engine LLM provider factory
  (opencode / ollama / omni_llm).
- `ADR-003-oc-pr-review-opencode-big-pickle.md` — `/oc` PR review GitHub Action uses a
  self-contained `opencode/big-pickle` workflow (OmniRoute deferred).
