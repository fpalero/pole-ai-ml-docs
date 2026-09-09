# ADR-005: Auto-disable expired Keycloak temp users via K8s CronJob

> This is a repo-wide architectural decision record. All ADRs live under
> `docs/decisions/`. The operator-facing design note + rollout runbook lives at
> `docs/dev-ops/keycloak-user-expiry/README.md`.

## Status
Accepted

## Date
2026-09-07

## Context

Staging evidence (2026-09-07, `pole-ai` realm): the temp account
`fpalero1986@gmail.com` sat `enabled` past its useful life with only `fe-user`
+ defaults roles — no `analyst-user`, so its actions were already role-blocked —
until the team-lead disabled it manually (`PUT enabled=false` + session kill).
Keycloak 26 provides **no native account-expiry**.

The existing app-side enforcement (`docs/app/keycloak/`, phases 2 + 8:
`pole_api` Redis `temp:*` markers, 2h window check, lazy purge + sweeper via the
`pole-api-admin` service account) only reaches users it has markers for
(`PAIML-KEYCLOAK-018…020`). If markers are absent or Redis state is lost, the
realm account lingers `enabled` forever. The user approved building an
automation with a 30-minute check interval.

## Decision

Disable past-due temp users with a dedicated **Kubernetes CronJob in the
`pole-ai-ml-infra` repo** (`*/30 * * * *`), driven by a Keycloak-native custom
user attribute **`account_expires_at` (ISO-8601 UTC)** set at enrollment, using
a single-purpose confidential client with only `realm-management →
manage-users`, secret in an operator-created K8s Secret, client-credentials
grant, disable + session-kill per match, stdout audit logging, and a
`DRY_RUN=true` log-only mode for rollout.

## Alternatives Considered

### In-app scheduler inside `pole_api`
- Pros: reuses the existing `pole-api-admin` client and sweeper code; one fewer
  moving part.
- Cons: hands **every API replica** privileged Keycloak credentials capable of
  disabling users — the secret fans out to all serving pods and couples realm
  hygiene to API uptime, scaling events, and deploy cadence. A crash-looping or
  scaled-to-zero API silently stops expiries with no independent signal.
- Rejected: privilege isolation outweighs code reuse here; expiry must survive
  the API being down.

### Extending the existing `pole_api` sweeper only (no Keycloak attribute)
- Pros: no realm-side contract, no new client.
- Cons: still Redis-marker-dependent — the exact gap this decision closes
  (users without markers are invisible to the sweeper). Adds no defense in
  depth.
- Rejected: does not cover the observed failure mode.

### Short token lifetimes alone (already in place, `PAIML-KEYCLOAK-004`)
- Pros: already shipped; bounds session usefulness.
- Cons: the account itself stays `enabled` and keeps obtaining fresh tokens on
  every login — exactly what staging demonstrated.
- Rejected as sufficient: complementary, not a substitute.

## Consequences

- Realm hygiene no longer depends on `pole_api` uptime or Redis durability; the
  expiry instant travels **with the user object** (`account_expires_at`), so any
  Admin API consumer enforces the same contract.
- New invariant to uphold forever: **users without `account_expires_at` are
  never touched** — ordinary accounts are safe by construction, and any
  attribute rename is a coordinated enrollment↔job change.
- New operational surface: one CronJob + one K8s Secret in `pole-ai-ml-infra`,
  audited via pod logs; secret rotation is a `kubectl`-only procedure (no code
  change).
- Rollout discipline is part of the decision: dry-run first, enforce after log
  review, permanent `DRY_RUN` toggle for future logic changes; 5-minute grace
  margin against clock skew; unparsable attribute values are skipped loudly,
  never acted on.
