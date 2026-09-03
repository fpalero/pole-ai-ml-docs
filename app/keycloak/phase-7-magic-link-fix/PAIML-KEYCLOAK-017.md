# Ticket: PAIML-KEYCLOAK-017

## Title
[Keycloak] Emergency probe fix: liveness-vs-boot crashloop relief + declarative startupProbe

## Description
During PAIML-KEYCLOAK-016 rollout, `kubectl rollout restart` crashlooped staging Keycloak: liveness budget ~150s < Quarkus boot ~104s + realm import, so the liveness probe killed the pod before it ever became ready. Live relief via `kubectl patch`: liveness `initialDelaySeconds` 90→300 + added `startupProbe`, after which the service went green. Declarative fix tracked as infra PR #27 (https://github.com/fpalero/pole-ai-ml-infra/pull/27, OPEN mergeable clean) with the same probe values. Post-relief verify: E2E magic-link 202 with synthetic address; live realm SMTP = Brevo confirmed via Admin API.

Why startupProbe (decision record):
- **initialDelay-only is fragile:** a fixed delay must cover the worst-case boot on every node; too short kills slow boots, too long delays failure detection forever.
- **startupProbe is correct:** it gates liveness/readiness until the app reports ready, with a generous `failureThreshold × periodSeconds` budget for slow Quarkus boot + import, then hands over to normal liveness. Declarative chart carries the same values as the live patch so the next rollout does not regress.

## Repository
pole-ai-ml-infra

## What to Do (Implementation Steps)
- [ ] Verify live relief: liveness `initialDelaySeconds=300` + `startupProbe` present via `kubectl describe deploy keycloak`; service green.
- [ ] Land declarative probe fix (infra PR #27) with identical values so future rollouts keep the boot budget.
- [ ] Re-run rollout guard: next `rollout restart` must complete without CrashLoopBackOff.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Staging Keycloak serves traffic (no crashloop) after the live patch.
- [ ] Declarative chart (PR #27 https://github.com/fpalero/pole-ai-ml-infra/pull/27) matches live relief values.
- [ ] E2E magic-link 202 with synthetic address; live SMTP = Brevo via Admin API.
- [ ] Documented boot budget: liveness ~150s < Quarkus ~104s + import, covered by startupProbe.

## Integration Tests to Run (Local Verification)
- [ ] `helm template` renders liveness delay 300 + startupProbe on the Keycloak Deployment.
- [ ] Live `kubectl get pods` shows Keycloak Ready after restart (record timings).

## Dependencies
- **Blocks:** None
- **Blocked By:** PAIML-KEYCLOAK-015

## Estimated Effort
- [S] (Small 1–2h)
