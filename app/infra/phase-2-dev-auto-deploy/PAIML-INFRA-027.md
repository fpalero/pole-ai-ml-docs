# Ticket: PAIML-INFRA-027

## Title
[CI/CD] Deploy staging with immutable short-sha image tag (fix helm no-roll on rolling 'develop' tag)

## Description
**ROOT CAUSE:** `pole-ai-ml` `.github/workflows/build-push.yml` `deploy-dev`
job dispatches `client-payload '{"tag": "<steps.meta.outputs.version>"}'`
which resolves to the rolling branch tag `develop`
(`docker/metadata-action` version output = `develop` for branch events).
`pole-ai-ml-infra` `.github/workflows/deploy-dev.yml` then runs
`helm upgrade --set pole-api.tag=develop` (same on `fe`/`analyst`). Because
the pod template image string never changes, the `helm upgrade` is a no-op
and the deployment NEVER rolls to the freshly pushed image — only a manual
`kubectl rollout restart` masks it.

Observed 2026-09-05: pod `pole-ai-pole-api-64d468c4d` remained on the
prior-day image after a green build+deploy; manual rollout was required; new
digest `sha256:9555b1d8…` only then rolled.

The short-sha tag (e.g. `pole-api:f01c7f8`) IS already pushed by the
build-push metadata action (verified: tags `develop` + `f01c7f8` on GHCR).

## Repository
pole-ai-ml (Step 1) + infrastracture / pole-ai-ml-infra (Step 2)

## What to Do (Implementation Steps)
- [ ] Step 1 [pole-ai-ml]: In `.github/workflows/build-push.yml` `deploy-dev`
      job, dispatch the immutable short sha, e.g. compute
      `SHA_SHORT="${GITHUB_SHA::7}"` and send
      `client-payload '{"tag": "<SHA_SHORT>"}'` (never the rolling
      `version`/`develop` tag). Add an explicit job output for the tag.
- [ ] Step 2 [infrastracture]: In `pole-ai-ml-infra`
      `.github/workflows/deploy-dev.yml` keep the guard/fallback semantics
      consistent — the `Set tag` step should use the dispatched payload as-is
      (immutable sha) and the existing `if empty → develop` fallback can
      remain as a safety default, but document that the sha must always be
      provided going forward. No other chart change required (values already
      reference `.tag`).
- [ ] Step 3: After merge + green CI, verify E2E: next `develop` merge →
      build-push auto (via `ML_REVIEW_PAT` now configured) → `deploy-dev`
      dispatch carries sha → `helm template` changes → pod rolls without
      manual intervention; record pod-old-digest vs new-digest + rollout
      status as evidence on the ticket.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `build-push.yml` `deploy-dev` dispatches an immutable short-sha tag
      (never the rolling `develop` tag); tag available as an explicit job
      output.
- [ ] `deploy-dev.yml` deploys the dispatched sha as-is; `develop` remains
      only as an empty-payload safety fallback, documented as such.
- [ ] E2E evidence on the ticket: next `develop` merge rolls the pod with no
      manual `kubectl rollout restart` (old vs new digest + rollout status).

## Integration Tests to Run (Local Verification)
- [ ] `actionlint` clean on `build-push.yml` + `deploy-dev.yml`.
- [ ] `helm template` diff: image string changes with the sha tag vs the
      previous `develop` no-op.
- [ ] End-to-end: merge to `develop` → build-push auto → deploy-dev dispatch
      carries sha → pod rolls without manual intervention; record
      pod-old-digest vs new-digest + rollout status.

## Dependencies
- **Blocks:** —
- **Blocked By:** PAIML-INFRA-026 (PAT + belt landed first — this closes the same loop's deploy half)
- **NOTE:** 026's belt cron activates only after manual `develop` → `main`
  promotion (default branch), but the PAT push-trigger path is live;
  INFRA-027 does not depend on that promotion.

## Estimated Effort
- [S] (Small < 1h)
