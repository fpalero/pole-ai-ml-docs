# Ticket: PAIML-INFRA-025

## Title
[Infrastructure] Fix deploy-dev & build-push workflows to check out `develop` instead of `main`

## Description
The CI deploy pipeline silently deploys the **wrong branch**. `infrastracture/.github/workflows/deploy-dev.yml` uses `actions/checkout@v4` with **no `ref:`**, so the job checks out the repo's **default branch (`main`)** instead of the integration branch `develop`. All feature work (e.g. the keycloak temp-access chart: Mailpit, theme, `pole-api-admin` client, env wiring) is merged into `develop` only. Every green deploy therefore re-deployed the **old chart from `main`**, leaving the staging stack stale for days while CI reported success.

Observed impact (2026-09-03 QA gate):
- Staging realm had no `pole-api-admin` client, no SMTP/Mailpit, no custom theme, no 2h token lifespan — even though all that was merged into `develop`.
- The same default-branch pitfall hit the manual dispatch of `Build & Push to GHCR`: `gh workflow run` without `--ref` used `main`, which would have tagged older code as `develop` (cancelled; re-dispatched with `--ref develop`).

## What to Do (Implementation Steps)
- [ ] Step 1: In `infrastracture/.github/workflows/deploy-dev.yml`, pin the checkout to the integration branch:
      `uses: actions/checkout@v4` → add `with: ref: develop`
- [ ] Step 2: Audit `infrastracture/.github/workflows/` for any other `actions/checkout@v4` without an explicit `ref` (e.g. `deploy-prod.yml`, `deploy-staging.yml`, `opencode.yml`) and pin each to its correct branch (`develop` for integration/staging, explicit `main` only for user-owned release flows).
- [ ] Step 3: Document the branch policy in the workflow comments or `infrastracture/README.md`: "CI deploys the integration branch (`develop`); `main` is user-owned manual release."
- [ ] Step 4: Consider hardening the build-push dispatch path so a `workflow_dispatch` with `tag=develop` never builds from `main`: either document `--ref develop` in the workflow_dispatch inputs help, or add an explicit guard/check step that fails if `github.ref` is `main` and the requested tag is `develop`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `deploy-dev.yml` checks out `ref: develop` (verified in the workflow YAML).
- [ ] No checkout in `infrastracture/.github/workflows/` silently uses the default branch where an explicit ref is intended.
- [ ] A manual `helm upgrade` from the `develop` chart produces the same result as the CI deploy (realm has `pole-api-admin`, Mailpit, theme, 2h lifespan, `KEYCLOAK_ADMIN_ISSUER` in-cluster).
- [ ] Branch policy is documented in the workflow/repo README.

## Integration Tests to Run (Local Verification)
- [ ] Local: `cd infrastracture && git checkout develop && ./scripts/deploy.sh` deploys the current `develop` chart (all keycloak temp-access resources present).
- [ ] CI simulation: from a branch other than `main`, trigger the deploy workflow and confirm the checked-out chart contains `charts/keycloak/templates/mailpit-deployment.yaml` (proves it did NOT use `main`).
- [ ] `helm --kube-context ipsf-server get values pole-ai -n pole-ai` shows `KEYCLOAK_ADMIN_ISSUER` in-cluster after a deploy.

## Dependencies
- **Blocks:** None (follow-up hardening; staging is already deployed manually with the correct chart)
- **Blocked By:** None

## Estimated Effort
- [S] (Small < 1h)