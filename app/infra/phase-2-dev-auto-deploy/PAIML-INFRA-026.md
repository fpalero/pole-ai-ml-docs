# Ticket: PAIML-INFRA-026

## Title
[CI] Fix /oc review merges not triggering build-push (GITHUB_TOKEN push suppression) + cron reconciliation

## Description
**ROOT CAUSE:** GitHub does not fire push-triggered workflows for pushes
created by `GITHUB_TOKEN` actions (except `workflow_dispatch` /
`repository_dispatch`). `.github/workflows/opencode.yml` runs
`anomalyco/opencode/github@latest` with `use_github_token: true` and
`GITHUB_TOKEN: ${{ github.token }}`. When the action merges a PR via
`gh pr merge --squash`, GitHub suppresses the `push` event that would
trigger `.github/workflows/build-push.yml` (trigger: push to `develop`), so
`build-push.yml` never runs after an `/oc review` merge. Both recent merges
(PR #230, #232) required manual `workflow_dispatch` to build.

## What to Do (Implementation Steps)
- [ ] Step 1: In `.github/workflows/opencode.yml`, make the merge step
      PAT-authenticated so the resulting push to `develop` carries a
      non-`GITHUB_TOKEN` identity and triggers `build-push.yml` push events.
      Either swap the whole action env to the PAT, or (cleaner) add an
      explicit post-review merge step using `secrets.<PAT_SECRET>` while the
      review itself keeps `GITHUB_TOKEN` — either is acceptable as long as
      the merge is PAT-authenticated and the intent is documented in the
      workflow comments. Prefer a dedicated secret `ML_REVIEW_PAT`
      (fine-grained or classic, with repo write on `pole-ai-ml`);
      `INFRA_PAT` is a candidate if its scope already covers `pole-ai-ml`
      repo write — verify scope before reusing.
- [ ] Step 2: Add `.github/workflows/build-reconcile.yml` (belt):
      `schedule` cron (e.g. every 15 min) + `workflow_dispatch` manual. The
      job checks the latest `develop` SHA's build-push run (`gh api
      repos/{owner}/{repo}/actions/workflows/build-push.yml/runs?head_sha=...`
      or equivalent); if no completed run exists for that SHA →
      `gh workflow run build-push.yml --ref develop` using `GITHUB_TOKEN`
      (`workflow_dispatch` IS permitted with `GITHUB_TOKEN` — the same
      exception that made our manual dispatches work). Permissions:
      `actions: write`, `contents: read`. Guard against duplicate concurrent
      dispatches (skip if a run for the SHA is already queued/in-progress).
- [ ] Step 3: Verify the `workflow_dispatch` trigger already present in
      `build-push.yml` is kept (it exists — manual dispatches worked).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] After merging a trivial PR via `/oc review`, `build-push.yml` starts
      automatically on the push (or the cron belt fires within 15 min); no
      manual dispatch needed.
- [ ] `actionlint` / workflow YAML syntax valid for both touched workflows.
- [ ] Suppression root cause documented in the workflow comments.

## Integration Tests to Run (Local Verification)
- [ ] `actionlint` clean on `opencode.yml` + `build-reconcile.yml`.
- [ ] Dry-run the reconcile check logic against a known-good SHA (read-only
      `gh api` call returns the expected completed run; no dispatch fired).
- [ ] End-to-end: merge a trivial PR via `/oc review` on a test branch and
      confirm `build-push.yml` triggers without manual intervention.

## Dependencies
- **Blocks:** None (independent; unblocks future 037 / any feature merges)
- **Blocked By:** None

## Estimated Effort
- [S] (Small < 1h)
