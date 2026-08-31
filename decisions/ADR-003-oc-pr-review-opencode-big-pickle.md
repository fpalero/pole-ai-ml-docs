# ADR-003: `/oc` PR review GitHub Action — opencode/big-pickle (self-contained)

> This is a repo-wide architectural decision record. All ADRs live under
> `docs/decisions/` (see `docs/decisions/ADR-001-crewai-implementation-flows.md`).

## Status
Accepted

## Date
2026-08-31

## Context

The `/oc` PR review GitHub Action is the team's automated code-review bot, shared across
the two pole-ai repositories. We need a single, reliable, self-contained workflow that
reviews a PR and, when the reviewer approves, merges it.

Investigation surfaced several failing configurations that had to be ruled out before a
working one was accepted:

1. **Cross-repo reusable workflow** between the two private repos
   (`pole-ai-ml` ↔ `pole-ai-ml-infra`) does not resolve on GitHub → immediate `failure`.
2. **Local reusable workflow** ref → `startup_failure`.
3. **OmniRoute routing** → `Model not found: auto/coding` / `invalid_api_key`: a fresh
   container has **no upstream provider configured**, so `auto/*` combos cannot resolve.
   `AUTH_ENABLED=false` and a native `OPENCODE_BASE_URL` did not fix it. This option is
   deferred (provisioning hooks preserved in
   `docs/dev-ops/opencode-omnirouter-api-reference.md`).
4. **`opencode/big-pickle`** (OpenCode's own free model) via the `OPENCODE_API_KEY` secret
   → **works**. Smoke test passed end-to-end.

## Decision

Restore the `/oc` GitHub Action to `opencode/big-pickle`, structured as **one
self-contained file** (`opencode.yml`) — no reusable workflow, no cross-repo dependency —
**duplicated in both** `pole-ai-ml` and `pole-ai-ml-infra`.

- **Model:** `opencode/big-pickle`
- **Auth:** `OPENCODE_API_KEY` GitHub secret (+ `GITHUB_TOKEN`)
- **Trigger:** `/oc` comment via `issue_comment` / `pull_request_review_comment`
  `types: [created]`; re-trigger requires a new comment. GitHub resolves the workflow from
  the **default branch**.
- **Behavior:** review-and-merge prompt; the bot reviews the PR and merges on approval.

## Consequences

- The two repos each carry an identical self-contained `opencode.yml`. No shared/reusable
  workflow to maintain across repos; updates must be applied to both copies.
- `.github/workflows/` in both repos now contains only `opencode.yml` (plus unrelated
  deploy/build workflows). Obsolete `opencode-omnirouter.yaml` / `opencode-reusable.yml`
  were deleted.
- Benign annotations remain: Node 20 deprecation + "cache write denied: token has no
  writable scopes". Neither affects the review/merge outcome.
- `main` is the default branch and hosts the workflow; every change still lands via a
  feature branch + PR into `develop` (then user-owned manual promotion to `main`).

## References

- Accepted smoke test: pole-ai-ml run `33399596897` on `main` @ `a39b6be` (all steps ✓, 2m52s).
- OmniRoute provisioning reference (deferred option):
  `docs/dev-ops/opencode-omnirouter-api-reference.md`.
