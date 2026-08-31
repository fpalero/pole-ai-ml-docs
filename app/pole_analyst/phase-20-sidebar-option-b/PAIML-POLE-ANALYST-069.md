# Ticket: PAIML-POLE-ANALYST-069

## Title
[Tests] Option-B E2E realignment — retire tab-bar expectations, triage detail-tab failures

## Description
Phase 20 (PLAN_PHASE_20.md). With Option B adopted (tab bar stays removed — ratifies parallel
commit 4d9666c), realign the E2E suite: rewrite/retire workflow-stitch-integration E2E-12a..15b
(Video-sections tablist expectations) into sidebar-driven flows (Library via sidebar; Analysis
History via Analysis item → /history; detail via history-row Open or direct URL), and triage the
workflow-tabs E2E-7/8/9 + workflow-coach failures on merged main (verify each against current UI;
fix selectors or flag genuine bugs — do not paper over real defects).

## What to Do (Implementation Steps)
- [ ] Rewrite 12a-c: sidebar-driven navigation assertions (Library page renders without tablist;
      Analysis routes to history page).
- [ ] Rewrite 13a/b: history table reached via sidebar Analysis item; Open → detail view.
- [ ] Rewrite 14a/b + 15a/b: detail-view assertions via direct navigation to an analyzed seeded
      video; gallery behind expander (Phase 17 composition).
- [ ] Triage workflow-tabs E2E-7/8/9 + coach C1-C3 on merged main with full env; classify
      selector-vs-defect; fix selectors, file defects for genuine bugs.
- [ ] Full isolated-config E2E run green (committed first-class harness:
      `playwright.config.isolated.ts` + `proxy.isolated.json`, ports 4300/8100,
      `_e2b` DBs — see `app/pole_analyst/e2e/README.md`).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Full analyst E2E suite green on merged main (0 failed; skips justified inline).
- [ ] No spec asserts the removed tab bar or Coach/upload sidebar entries.

## Integration Tests to Run (Local Verification)
- [ ] `npx playwright test -c playwright.config.isolated.ts` (full) — committed
      isolated harness (`playwright.config.isolated.ts` + `proxy.isolated.json`,
      FE `:4300` / BE `:8100`, `_e2b` DB suffix). Shell env:
      `E2E_API_BASE=http://localhost:8100`,
      `MONGODB_URI=mongodb://admin:password@localhost:27017/?authSource=admin`,
      `SKELETON_DB=skeleton_data_e2b`, `ANALYSIS_DB=analysis_ai_e2b`
      (`POLE_API_DB=pole_api_e2b` and `E2E_FAKES=1` are pinned inside the
      config's webServer). Full procedure incl. cleanup:
      `app/pole_analyst/e2e/README.md` ("Isolated E2E runs").

## Dependencies
- Blocked By: PAIML-POLE-ANALYST-068 · Blocks: none · Effort: [M]
