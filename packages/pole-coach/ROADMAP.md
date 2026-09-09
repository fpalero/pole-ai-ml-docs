# Roadmap — `pole_coach` implementation order & gates

Sequencing, per-ticket gates, and rollback for `PAIML-POLE-COACH-001..006`.
Phase scope lives in `PLAN.md`; repo-wide placement in `docs/ROADMAP.md` (Tier 1b).

## Lanes
- **Lane 1 (sequential):** 001 scaffold/scraper/catalog → 002 state+nodes+contracts →
  003 graphs+supergraph+router.
- **Lane 2 (sequential, after Lane 1):** 004 analyst wiring+profile+biomech →
  005 integration+E2E+docs.
- **Lane 3 (branches after 001+002, lands last):** 006 translation (extends 005's gate).

## Gate per ticket
1. `crew-validate` on the phase folder + cleanup worktrees.
2. Isolated worktree + `feature/PAIML-POLE-COACH-<NNN>-<slug>` from `develop`.
3. Full phase scope + unit tests (`pixi run test-pole-coach` or subset).
4. Push, PR vs `develop`, `/oc review`, CI green, merge.
5. `doc` incremental RAG refresh + manifest commit.
6. **Start the integration test** and report; dependents start only on MERGED + green.

## Milestones
- **M1** — 001 merged: catalog + scaffold (RAG-independent asset).
- **M2** — 002 merged: node contracts frozen (graphs unblocked).
- **M3** — 003 merged: supergraph routes all 7 flows standalone.
- **M4** — 004 merged: analyst chat answers via supergraph (first user-visible change).
- **M5** — 005 merged + QA gate GREEN on staging (`*_test` DBs): handover for manual acceptance.
- **M6** — 006 merged + extended gate GREEN: done (report, stop; `develop`→`main` user-owned).

## Coexistence & rollback
- Separate track from in-flight `-101`/`-076`; rebase each worktree on latest `develop`.
- `chatbot` + `training_chatbot` untouched; `pole_fe` untouched; Helm changes in `pole-ai-ml-infra`.
- Rollback: tag `pole-ai-v1` on `origin/develop` in all three repos.

## Verification
`pixi run test-pole-coach` · `pixi run test-api` · `pixi run test-chatbot` ·
`pixi run test-integration` · `pixi run pole-analyst-e2e` · `pixi run eval-coach-grounding`.
