---
# Ticket: PAIML-POLE-API-120

## Title
BE PR checks gate + workflow_run-triggered review-merge (auto-flow)

## Status
📋 PLANNED

## Description
The opencode review action cannot complete: `opencode.yml` orders the
agent to judge "broken tests" / "failing CI" while zero BE checks exist,
so the agent runs suites itself (observed 21:46–21:53Z: repeated pytest
with hand-built PYTHONPATH) and dies at `timeout-minutes: 15`
(`.github/workflows/opencode.yml:40`). Two `/oc review` runs on #311
both cancelled at ~16:00 wall with no review posted.

Agreed design, user-confirmed ("option C"): be-checks executes first on
PRs against `develop`; when its checks finish green, `opencode.yml` is
triggered immediately via `workflow_run` (no comment round-trip, no PAT
needed for triggering, no loop risk — a later job in the same run is
NOT used; review logic stays solely in `opencode.yml` so manual `/oc`
and auto share one prompt). The agent verifies all-green (real
`gh pr checks` + clean diff) and on green performs approve + squash
merge itself (existing agent-merge behavior kept, PAT identity so
`build-push` fires).

- [ ] New `.github/workflows/be-checks.yml` (test jobs ONLY — review
      lives in `opencode.yml`): `on: pull_request` with paths
      `app/pole_api/**`, `packages/pole_coach/**`, `packages/chatbot/**`,
      `.github/workflows/be-checks.yml`; `concurrency` group
      `be-checks-${{ github.ref }}` with `cancel-in-progress: true`;
      `runs-on: self-hosted`; jobs `lint` (`pip install ruff` +
      `ruff check`), `unit-polecoach` (`pixi run test-polecoach`),
      `unit-api` (`pixi run test-api` excluding `tests/analysis`,
      `tests/test_e2e.py`, `tests/test_analyst_ws_integration.py` —
      unscoped hangs >15 min), `unit-chatbot` (`pixi run test-chatbot`);
      per-job `timeout-minutes: 25`.
- [ ] `opencode.yml`: (a) Scope block making review READ-ONLY — read diff
      + related source only; consult `gh pr checks <n>` as the test
      verdict; never pytest / pixi run / npm test or equivalents
      (exact block below); (b) add `workflow_run` trigger (`workflows:`
      = exact `name:` of be-checks, `types: [completed]`); (c) rework job
      gating to run the review path on EITHER manual `/oc` comment OR
      `workflow_run` with conclusion `success` whose associated PR
      targets `develop`; resolve the PR number from the event
      (`issue.number` vs `workflow_run.pull_requests[0].number`;
      fail closed when no PR is associated); (d) dedupe: skip when a
      completed opencode run already exists for the head SHA (same SHA
      reviewed twice = waste; new SHA = new review); (e) diff-size cap:
      over ~400 changed lines → approve-only, human merges.
      Scope block:
      ```yaml
      Scope: this is a READ-ONLY code review. Read the PR diff and related
      source files only. Before deciding, run `gh pr checks <PR-number>` and
      treat its result as the test verdict. Do NOT run tests, builds, linters,
      or any command that executes project code — judge test impact by reading
      the diff and the reported check results. Never pytest, pixi run, npm test,
      or equivalents.
      ```
- [ ] Out of scope: branch-protection flip (owner manual: require new
      checks on `develop`), machine-user PAT (future — kills the
      author-PAT `--request-changes` wart), timeout bump (unnecessary
      once reviews stop executing tests).
- [ ] Sequencing note (critical): `workflow_run`- AND `issue_comment`-
      triggered workflows execute from the DEFAULT branch (`main`) — the
      `opencode.yml` half goes live only after a `develop` → `main`
      promotion (user-owned manual release). `be-checks.yml` (a
      `pull_request` workflow) works immediately from its own PR via the
      merge ref. Until promotion: PRs get checks but no auto-review
      (manual `/oc` still works, still flaky).

## Files Affected
- `.github/workflows/opencode.yml` (Scope block + `workflow_run`
  trigger + gating/dedupe/cap)
- `.github/workflows/be-checks.yml` (new, test jobs only)

## Unit-Test Requirement
- [ ] N/A (CI config) — validation is live: the PR triggers be-checks
      on itself (workflow path included) and must go green. Full
      auto-flow proof comes on the NEXT PR after promotion (this PR
      predates the live trigger).

## Integration Tests
- [ ] be-checks green on its own PR (lint + 3 unit jobs).
- [ ] Post-promotion: a BE PR gets an automatic review citing checks,
      no test execution in its log.

## Acceptance Criteria
- [ ] Reviews complete in minutes citing `gh pr checks`, never executing suites.
- [ ] BE PRs report checks; green + clean auto-flow reaches squash merge.
- [ ] Docs-only PRs unaffected (no be-checks run → no auto-review).

## Dependencies
- **Blocks**: none.
- **Blocked By**: none.

## Estimated Effort
- [S]
---
