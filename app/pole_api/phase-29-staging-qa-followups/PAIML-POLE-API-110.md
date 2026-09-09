# Ticket: PAIML-POLE-API-110

## Title
Coach catalog stores: trick_catalog Mongo collection + separate catalog RAG

## Description
User-decided (2026-09-09, six prior confirmations + catalog RAG-vs-Mongo
decision) follow-up to the 007 gate evidence. The source of truth stays
`packages/pole_coach/trick_catalog.json` (447 moves, versioned in repo).
BOTH stores in this ticket are derived — re-seed/re-index on catalog updates,
never hand-edit.

Locked decisions (user-approved):
1. **Mongo is exact-reads, RAG is semantic.** Mongo `trick_catalog` serves
   exact reads/gates; the separate catalog RAG serves semantic
   ("moves like X") queries. Neither replaces the versioned JSON.
2. **Canonical collection name is `trick_catalog`** (user said
   "tricks catalog" — code name `trick_catalog`).
3. **Catalog RAG is coach-owned on existing infra** — a separate Chroma
   collection for the catalog (e.g. `trick_catalog` alongside the existing
   `pole_rag` collections: `text_chunks` + `image_descriptions`), same infra,
   no new infra. Coach queries catalog-first for transitions/progressions,
   falls back to the pole-agent RAG for deep technique.
4. **Extend existing `RAGProvider` protocols, don't redesign**
   (`pole_coach/protocols.py` + `pole_rag` `ChromaStore`/`query` conventions).
5. **Constrained drill pick unchanged** (108 behavior preserved).
6. This work is a **new ticket** (not 107, not 108).

`pole_coach` stays langchain-free; new stores are consumed on the
`app/pole_api` analyst/coach path.

## Evidence (007 ticket gate runs)
Source: `packages/pole-coach/phase-5-integration-tests-e2e/PAIML-POLE-COACH-007.md`.

- Gate runs (SAMPLE-5, 2026-09-09) showed the readiness
  "No catalog entry" short-circuit (`graphs/readiness.py` unknown-status path)
  killing 4/5 RE turns: the JSON catalog exists but the read path has no
  seeded Mongo collection to resolve known slugs against. This ticket fixes
  the read path (seeded `trick_catalog`) plus semantic catalog recall
  (1-chunk-per-trick catalog RAG).

## What to Do (Implementation Steps)
- [ ] (1) **NEW Mongo collection `trick_catalog` + seed procedure.** Fields:
  `slug, names/aliases, difficulty, category, pso_level, transitions,
  image_file, page_url`. Seed from `packages/pole_coach/trick_catalog.json`
  (447 docs; moves carry `slug, name, alternate_names, difficulty,
  pso_level, category, description, image_file, page_url, transitions[]`).
  One-time seed + deploy/startup step so fresh DBs get it. Derived store —
  re-seed on catalog updates, never hand-edit.
- [ ] (2) **Separate catalog Chroma collection (coach-owned, same infra).**
  1-chunk-per-trick (`name + aliases + description + transitions`), indexed
  from the same JSON. Check `pole_rag` conventions (`config.py`
  `COLLECTION_TEXT/COLLECTION_IMAGE`, `chroma_store.py`, `query.py`) and
  extend — no new infra, no redesign of `RAGProvider`.
- [ ] (3) **Wiring: readiness + progress flows.** Readiness/progress use Mongo
  for exact reads/gates (replaces the "No catalog entry" short-circuit for
  known slugs); catalog-RAG for semantic transition/progression queries
  ("moves like X"); fallback to pole-agent RAG for deep technique.
  Constrained drill pick (108) unchanged.
- [ ] (4) **Unit tests for repo/read-path/indexing** (seed count, slug
  resolution, chunk-per-trick indexing, catalog-first/fallback routing).
- [ ] (5) Re-run the affected test files green.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] (1) Catalog collection seeded (447 docs) + readiness resolves known
  slugs (no "No catalog entry" short-circuit for catalogued tricks).
- [ ] (2) Catalog-RAG returns the right trick top-1 for alias/transition
  queries.
- [ ] (3) 25-gate readiness green on the catalog-backed read path.
- [ ] (4) Unit tests for repo/read-path/indexing green.

## Out of Scope (explicitly out — separate decisions pending)
- 107 fail-safes (terminal fallback frame + deterministic disclaimer —
  `PAIML-POLE-API-107.md`, separate ticket; reference, do not re-implement).
- 006 decision / translation.
- FE work.
- Full-150 run.

## Integration Tests to Run (Local Verification)
- [ ] Seed test: `trick_catalog` holds 447 docs with the required fields;
  fresh-DB seed path verified.
- [ ] Read-path test: readiness resolves known slugs (alias + canonical)
  instead of short-circuiting to unknown.
- [ ] Catalog-RAG test: alias/transition query returns the right trick top-1;
  catalog-first, pole-agent fallback for deep technique.
- [ ] 25-gate readiness suite green on the catalog-backed path.
- [ ] `pixi run test-api` (full task — must stay GREEN).

## Unit-Test Requirement
- [ ] Repo test: seed count/fields asserted against the JSON (447 docs).
- [ ] Read-path test: known slugs (canonical + alias) resolve; unknown slugs
  still short-circuit explicitly.
- [ ] Indexing test: 1-chunk-per-trick with name/aliases/description/
  transitions content; top-1 alias/transition assertions.

## Dependencies
- **Blocks**: 25 re-run green.
- **Blocked By**: — (standalone; 108 merged).

## Estimated Effort
- [M]

## As-built deviations

### Rebase onto 108 tip
- Branch cut from stale fc04c80 (missing 108/109); rebased cleanly onto 2c9e521 — no conflicts, disjoint hunks.
- Deviation 1 resolved: progress gates now accept injected Mongo catalog dict via facade thread-through; static-JSON behavior byte-identical when omitted.
- 4 new tests (18 total). HEAD 20d821b.
