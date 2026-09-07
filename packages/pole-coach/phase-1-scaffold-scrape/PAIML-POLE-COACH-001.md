# PAIML-POLE-COACH-001 — Phase 1 (A): scaffold + polemovebook scraper + trick catalog

- **Status:** 📋 PLANNED
- **Blocks:** PAIML-POLE-COACH-002, PAIML-POLE-COACH-003, PAIML-POLE-COACH-004, PAIML-POLE-COACH-005
- **Blocked By:** —

## Goal
Create `packages/pole_coach` (Option A layout — `src/pole_coach/`, PYTHONPATH, no
pyproject, mirrors `pole_rag`) and a facts+description+image scraper for
`polemovebook.com` that produces a versioned `trick_catalog.json` (+ `images/`) and a
curated `slug → trick_label` alias map, feeding Phase 3 readiness/progression.

## Architectural context
- **Database:** no new DB. Catalog is a checked-in JSON
  (`packages/pole_coach/trick_catalog.json`) + `packages/pole_coach/images/` folder.
  Alias map is a curated Python/JSON table mapping PMB slugs
  (e.g. `shoulder-mount`) to pipeline `trick_label` vocabulary
  (e.g. `shoulder_mount`).
- **Layout:** Option A (`pole_rag`-style): `python -m` entry points, `PYTHONPATH=src`,
  no console scripts, no pyproject. `beautifulsoup4` → root `[pypi-dependencies]`
  (precedent: pillow/pymupdf for `pole_rag`); `httpx`/`langgraph` already in the env.
- **Caching/performance:** scraper is an offline CLI (`pixi run scrape-polecoach`); no
  runtime fetch. Honest UA + ≥1s delay between pages.
- **Scalability/resilience:** ~500 `/movepage/<slug>` pages from `sitemap.xml`; resume on
  failure (skip already-fetched slugs), structured per-page errors, never crash the run.
- **External:** `https://polemovebook.com` (+ `sitemap.xml`). No auth. Respects rate limits.

## Scope (in)
1. `packages/pole_coach/src/pole_coach/` layout (`__init__.py`, `nodes/`, `graphs/`,
   `tools/`); `beautifulsoup4` added to root `[pypi-dependencies]`; no pyproject;
   `pixi install` green.
2. `src/pole_coach/tools/scrape_polemovebook.py` (run via `python -m`) — per move
   extracts: `name`, `alternate_names`, `difficulty`
   (Intro/Beginner/Intermediate/Advanced/Extreme), `pso_level` (L1–L5), `category`,
   **description (prose)**, **picture (image URL → `images/<slug>.webp`)**,
   and **progression** (`transitions-into` edges: target slug + level).
3. `trick_catalog.json` schema validation (required keys, levels in enum, transitions
   reference known slugs) + `slug → trick_label` alias map (manual, reviewable).
4. Unit tests: HTML-parse fixtures (no network), catalog schema validation, dangling
   transition refs rejected, alias-map coverage for the classifier's `trick_label` set.

## Scope (out)
Graph code, nodes, RAG seeding from scraped prose (future), FE.

## Tasks
- 1.1 Scaffold `packages/pole_coach` (`src/pole_coach/__init__.py`, no pyproject) +
  root `beautifulsoup4` dep; verify import with `PYTHONPATH=src`.
- 1.2 Implement the scraper (sitemap → slugs → per-page parse → JSON + images) with
  resume/skip, honest UA, delay, per-page `{"error"}` records.
- 1.3 Add `pixi run scrape-polecoach` + `pixi run test-polecoach` tasks (mirror
  `rag-seed`/`test-rag`: `cwd = "packages/pole_coach"`, `env = { PYTHONPATH = "src" }`).
- 1.4 Author the `slug → trick_label` alias map against the classifier vocabulary.
- 1.5 Unit tests (parse fixtures, schema, dangling refs, alias coverage).

## Acceptance
- [ ] `pixi run scrape-polecoach` produces a schema-valid `trick_catalog.json`
  (≥400 moves) + `images/` without crashing on malformed pages.
- [ ] Every `transitions` target resolves to a known slug; every classifier
  `trick_label` has an alias entry.
- [ ] Unit suite green (`pixi run test-polecoach`).

## Verification
`pixi install`, `pixi run scrape-polecoach --help`, `pixi run test-polecoach`.
Then **start the integration test** per ticket DoD.

## Risks
- PMB ToS/robots.txt disallow AI bots; images/prose are their copyrighted content.
  Confirm redistribution rights before any public deploy. Scraper uses honest UA +
  rate limiting; no credentialed/JS-gated endpoints touched.
- PMB slug renames break transitions; mitigated by the dangling-ref validator.

## Definition of Done
Unit suite green → run the integration aggregator (`pixi run test-integration` smoke)
and report. No implementation beyond this ticket's scope starts.
