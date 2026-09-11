# Ticket: PAIML-POLE-API-119

## Title
BE PR checks gate + inline review-merge (auto-flow)

## Status
📋 PLANNED

## Description
The opencode review action cannot complete: `opencode.yml` orders the
agent to judge "broken tests" / "failing CI" while zero BE checks exist,
so the agent runs suites itself (observed 21:46–21:53Z: repeated pytest
with hand-built PYTHONPATH) and dies at `timeout-minutes: 15`
(`.github/workflows/opencode.yml:40`). Two `/oc review` runs on #311
both cancelled at ~16:00 wall with no review posted.

Agreed design (user-confirmed): when be-checks finishes green, an inline
review job executes the opencode review; the agent verifies all-green
(real `gh pr checks` results + clean diff) and on green performs approve
+ squash merge itself (existing agent-merge behavior kept, PAT-identity
so `build-push` fires).

- [ ] `opencode.yml` prompt: add a Scope block making review READ-ONLY —
      read diff + related source only; consult `gh pr checks <n>` as the
      test verdict; never pytest / pixi run / npm test or equivalents.
      Exact block:
      ```yaml
      Scope: this is a READ-ONLY code review. Read the PR diff and related
      source files only. Before deciding, run `gh pr checks <PR-number>` and
      treat its result as the test verdict. Do NOT run tests, builds, linters,
      or any command that executes project code — judge test impact by reading
      the diff and the reported check results. Never pytest, pixi run, npm test,
      or equivalents.
      ```
- [ ] New `.github/workflows/be-checks.yml`: `on: pull_request` with paths
      `app/pole_api/**`, `packages/pole_coach/**`, `packages/chatbot/**`,
      `.github/workflows/be-checks.yml`; `concurrency` group
      `be-checks-${{ github.ref }}` with `cancel-in-progress: true`;
      `runs-on: self-hosted`; jobs `lint` (`pip install ruff` +
      `ruff check`), `unit-polecoach` (`pixi run test-polecoach`),
      `unit-api` (`pixi run test-api` excluding `tests/analysis`,
      `tests/test_e2e.py`, `tests/test_analyst_ws_integration.py` —
      unscoped hangs >15 min), `unit-chatbot` (`pixi run test-chatbot`);
      per-job `timeout-minutes: 25`.
- [ ] Final `review` job in the same file: `needs` all test jobs,
      `if: success()`; minimal permissions (`contents: read`,
      `pull-requests: write`); merge-token resolution step copied from
      `opencode.yml` (ML_REVIEW_PAT preferred, github.token fallback);
      checkout PR head; run `anomalyco/opencode/github@latest` with the
      review prompt + Scope block + approve-and-squash-merge-on-green
      instruction (mirror `opencode.yml` decision block). Review hiccups
      must use `continue-on-error: true` so they never red a green test gate.
- [ ] Out of scope: branch-protection flip (owner manual: require new
      checks on `develop`), machine-user PAT (future — kills the
      author-PAT `--request-changes` wart), timeout bump (unnecessary
      once reviews stop executing tests).
- [ ] Sequencing note: `issue_comment` workflows execute from the DEFAULT
      branch — the prompt fix goes live only after a `develop` → `main`
      promotion (user-owned manual release).

## Files Affected
- `.github/workflows/opencode.yml` (prompt Scope block only)
- `.github/workflows/be-checks.yml` (new, incl. inline review job)

## Unit-Test Requirement
- [ ] N/A (CI config) — validation is live: the PR triggers be-checks
      on itself (workflow path included) and must go green; the inline
      review must complete citing checks. NOTE: if the PR is itself
      clean+green, the flow may squash-merge it automatically — intended
      dogfood of this exact ticket.

## Integration Tests
- [ ] be-checks green on its own PR (lint + 3 unit jobs).
- [ ] Inline review completes without test execution in its log.

## Acceptance Criteria
- [ ] `/oc`-style reviews complete in minutes citing `gh pr checks`.
- [ ] BE PRs report checks; green + clean auto-flow reaches squash merge.
- [ ] A review hiccup never reds a green test gate (`continue-on-error`).

## Dependencies
- **Blocks**: none.
- **Blocked By**: none.

## Estimated Effort
- [S]
