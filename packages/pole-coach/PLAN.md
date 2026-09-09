# Implementation Plan — `pole-coach` (LangGraph multi-agent virtual coach)

Multi-agent LangGraph coach: reusable nodes (Pole / Biomechanics / Coach + retrieval /
metrics / router / formatter), named graphs per flow, and a supergraph with an LLM
intent router. New layer consumed by the pole-analysis FE chatbot (`analyst_chatbot`
slice). Scraped `trick_catalog.json` (polemovebook, facts + description + images)
feeds readiness/progression.

> Source of truth for flow semantics: `MainState`, per-agent I/O schemas, and the
> 7 graphs (`video_analysis`, `progress`, `query`, `training_plan`, `injury`,
> `improve_trick`, `readiness`).

## Phases and state

| Phase | Ticket | Scope | State |
|---|---|---|---|
| 1 (A) | [PAIML-POLE-COACH-001](phase-1-scaffold-scrape/PAIML-POLE-COACH-001.md) | `packages/pole_coach` scaffold (Option A: `src/`, PYTHONPATH, no pyproject — mirrors `pole_rag`) + facts+desc+image scraper + `trick_catalog.json` + alias map | ✅ DONE |
| 2 (B) | [PAIML-POLE-COACH-002](phase-2-nodes/PAIML-POLE-COACH-002.md) | State schema + 7 nodes (own file each) + protocols | ✅ DONE |
| 3 (C) | [PAIML-POLE-COACH-003](phase-3-graphs-supergraph/PAIML-POLE-COACH-003.md) | 7 graphs + supergraph + LLM intent router | ✅ DONE |
| 4 (D) | [PAIML-POLE-COACH-004](phase-4-integration/PAIML-POLE-COACH-004.md) | `analyst_chatbot` wiring + profile extension + Phase-33 biomech + angle fix | ✅ DONE |
| 5 (E) | [PAIML-POLE-COACH-005](phase-5-integration-tests-e2e/PAIML-POLE-COACH-005.md) | Integration tests + analyst E2E + docs | 🟡 PARTIAL — code done, PR pending; docs close-out (5.3) in progress, QA gate (5.4) pending |
| 6 (F) | [PAIML-POLE-COACH-006](phase-6-translation/PAIML-POLE-COACH-006.md) | Translation layer (Hy-MT2 + glossary + cache, no new infra) | 📋 PLANNED |

Dependency chain: 001 → 002 → 003 → 004 → 005, plus 006 (translation, after 001+002; extends 005's gate).

## Rollback point

Tag `pole-ai-v1` on `origin/develop` in **all three repos** (`pole-ai-ml`, `pole-ai-ml-docs`,
`pole-ai-ml-infra`) marks the pre-`pole-coach` state. Roll back with
`git reset --hard pole-ai-v1` (local) / `git push origin pole-ai-v1` already on remote.
