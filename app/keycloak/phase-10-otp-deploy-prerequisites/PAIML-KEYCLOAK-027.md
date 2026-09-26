# Ticket: PAIML-KEYCLOAK-027

## Title
[Infra][Keycloak] Confirm Direct Access Grants enabled on `pole-fe` / `pole-analyst` across every environment (live-realm proof, not repo state)

## Description
After `verify-code`, `pole_api` mints the Keycloak session with a
**hidden-password Direct Access Grant** (`grant_type=password` against the
enrolled app client). Keycloak rejects a Direct Access Grant when the client has
`directAccessGrantsEnabled: false`, so the flow cannot complete without it.

**This ticket is a verification-and-repair ticket, not a blind "turn it on".**
The blocker was originally recorded as "Direct Access Grants must be enabled"
from a Phase 9 code reading, before the realm was inspected. Checking the
actual sources on 2026-09-26 shows the declarative config already carries it:

| Source | `pole-fe` | `pole-analyst` |
| :--- | :--- | :--- |
| `helm/pole-ai/charts/keycloak/templates/configmap.yaml` (embedded realm) | `directAccessGrantsEnabled: true` | `directAccessGrantsEnabled: true` |
| `keycloak/realm-pole-ai.json` (standalone realm) | `true` | `true` |
| Live local realm (Admin API, read 2026-09-26) | `true` | `true` |

So the **repo state is already correct and the local QA environment already
satisfies this blocker** — which is exactly why the local `PAIML-KEYCLOAK-024`
run passes. What is **unproven** is the *deployed* environments: a realm that
was imported once from an older ConfigMap and never re-synced can still carry
`false` in its live DB, because `--import-realm` only imports realms that **do
not already exist** in the dev-file PVC (the exact reason the `realm-sync`
Job, `PAIML-INFRA-036/037`, exists).

This ticket therefore owns:
1. **Proving** the live client config in each deployed environment via the
   Admin API (repo state is not evidence of live state).
2. **Repairing** any environment that drifted, via the declarative sources
   (never a live-console-only fix, which would be undone by the next realm-sync).
3. Keeping the two declarative sources in agreement so the drift cannot recur.

**Decision record (declarative, not console).** A live Admin API `PUT` is
rejected as a fix: `realm-sync` runs on every `post-install`/`post-upgrade` and
does `partialImport` of clients with `policy: OVERWRITE` from the mounted realm
ConfigMap, so a console-only change is reverted on the next deploy. The fix must
land in the chart ConfigMap (and the standalone `keycloak/realm-pole-ai.json`,
which is the operator-facing source referenced by `infrastracture/keycloak/README.md`),
then propagate through realm-sync.

## Repository
pole-ai-ml-infra

## What to Do (Implementation Steps)
- [ ] Read each deployed realm's live client config via the Keycloak Admin API
  (`GET /admin/realms/pole-ai/clients?clientId=pole-fe` and `...=pole-analyst`)
  and record `directAccessGrantsEnabled` per environment (local, dev/staging,
  prod). **Redact tokens in any evidence.**
- [ ] Where an environment reads `false`, fix it **declaratively**: confirm the
  chart ConfigMap block for that client renders
  `"directAccessGrantsEnabled": true` and that the standalone
  `keycloak/realm-pole-ai.json` agrees; then let the `realm-sync` Job apply it
  (`policy: OVERWRITE`) and re-read the live value to confirm it flipped.
- [ ] Where the live value is already `true`, record it as **verified-no-change**
  (this is the expected outcome for the local QA environment) and change no
  chart value — do not churn the realm JSON for a non-problem.
- [ ] Verify the two declarative sources stay **byte-consistent** on the client
  block (the embedded ConfigMap realm and `keycloak/realm-pole-ai.json`); if
  they disagree, reconcile and note which is authoritative in
  `infrastracture/keycloak/README.md`.
- [ ] Confirm `realm-sync` is `enabled: true` in the target environments — if it
  is disabled, the declarative change cannot reach the live realm at all, and
  that is the real defect to fix.
- [ ] Note the security trade-off in the PR description: Direct Access Grants on
  a **public** client means the password grant endpoint is reachable for those
  client IDs. It is required only because Phase 9 ships the hidden-password
  grant (ADR Decision 2, `PLAN_PHASE_9.md`); ticket `PAIML-KEYCLOAK-025` removes
  the mechanism via token exchange, at which point this grant can be turned back
  off. Do **not** disable it while 025 is outstanding.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] A recorded Admin API read per environment proving
  `directAccessGrantsEnabled == true` on **both** `pole-fe` and `pole-analyst`
  (evidence attached; tokens redacted).
- [ ] Any environment that was `false` is now `true` **via the declarative
  sources**, and the value survives a `realm-sync` re-run (not a console-only
  edit).
- [ ] The embedded chart realm and `keycloak/realm-pole-ai.json` agree on the
  client block; `realm-sync.enabled: true` in every target environment.
- [ ] Environments already correct are recorded as verified-no-change with no
  gratuitous realm churn.
- [ ] The Phase 9 note that Direct Access Grants stay enabled **only** until
  ticket 025 is recorded in the PR body.

## Integration Tests to Run (Local Verification)
- [ ] `helm lint helm/pole-ai` + `helm upgrade --dry-run` — the rendered realm
  contains `"directAccessGrantsEnabled": true` for both app clients.
- [ ] Admin API read-back per environment (see above) with values redacted.
- [ ] Functional probe (local): a Direct Access Grant against `pole-fe` with
  bogus credentials returns an **auth error**, not
  `unauthorized_client` / "Direct grant is not allowed" — proving the grant
  type is enabled without proving any credential.
- [ ] Re-run `realm-sync` and re-read: the value must not revert.

## Dependencies
- **Blocks:** PAIML-KEYCLOAK-024 (QA gate)
- **Blocked By:** None

## Estimated Effort
- [S] (Small 1–2h) — mostly verification; small if drift is found
