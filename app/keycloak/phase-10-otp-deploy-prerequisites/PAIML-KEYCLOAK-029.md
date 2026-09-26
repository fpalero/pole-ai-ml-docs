# Ticket: PAIML-KEYCLOAK-029

## Title
[Infra][Gate] OTP deploy-prerequisite matrix in dev/staging/prod — close the Phase 9 rollout gap before any deployed QA claim

## Description
This is the **rollout gate** for Phase 10. 026–029 make the prerequisites real;
this ticket is what stops the team from *claiming* the flow works in a deployed
environment before 026–028 have actually landed and been observed there.

**The gap this exists to close, stated plainly.** The Phase 9 QA gate
(`PAIML-KEYCLOAK-024`) is being run **locally**, with the pepper, host map and
Brevo key provisioned in the local stack. A green local run therefore proves the
*code* path, and proves **nothing** about a deployed environment. As of
2026-09-26 the live `pole-api` ConfigMap in the local cluster carries only
`TEMP_ACCESS_COOLDOWN_S` / `WINDOW_S` / `TOKEN_TTL_S` / `SWEEPER_INTERVAL_S` —
`TEMP_ACCESS_OTP_PEPPER`, `FE_BASE_URL`, `ANALYST_BASE_URL` and `BREVO_API_KEY`
are wired in **no** environment. Every deployed environment would answer **503**
on the OTP endpoints today.

Consequences of not having this gate (the reasons it is a ticket, not a note):
- **A green local `PAIML-KEYCLOAK-024` gets reported as "Phase 9 works"**, and
  that is false for dev/staging/prod. This ticket makes the environment matrix
  the thing that is signed off, so the report cannot be silently wrong.
- **Fail-closed 503s are invisible in a smoke test** that only asserts "not a
  5xx-crash" or that skips the OTP hop. A prerequisite sweep that greps the
  rendered manifests catches it.
- **Per-environment drift** (right values in staging, missing in prod) is the
  common case, and is only visible when each environment is checked separately.

**Decision record (what "deployed" means here).** The gate is over
**deployed environments** (dev/staging/prod) — the local sandbox is where
`PAIML-KEYCLOAK-024` runs and is explicitly *not* the proof. A "deployed
environment" is one where the manifest is rendered by the deploy workflow from
the Actions secret store; a hand-edited local override does not count, because
it is not reproducible from the repo.

## Repository
pole-ai-ml-infra

## What to Do (Implementation Steps)
- [ ] Build a per-environment prerequisite matrix over dev/staging/prod with one
  row per requirement, recording **actual observed state** (not intent):

  | Requirement | Source of truth | Ticket |
  | :--- | :--- | :--- |
  | `TEMP_ACCESS_OTP_PEPPER` in `pole-api` Secret | live Secret key list | 026 |
  | Direct Access Grants on `pole-fe` + `pole-analyst` | live realm, Admin API | 027 |
  | `FE_BASE_URL` + `ANALYST_BASE_URL` in `pole-api` ConfigMap | live ConfigMap | 028 |
  | `BREVO_API_KEY` in `pole-api` Secret | live Secret key list | 028 |

- [ ] For each environment, render the manifests (`helm template`, and the real
  live object) and assert: the pepper and Brevo key are in the **Secret** only;
  both URLs are in the **ConfigMap** with the values from the per-environment
  table in 028 (not the demo hosts leaking into prod).
- [ ] Assert `realm-sync.enabled: true` and the two app clients'
  `directAccessGrantsEnabled: true` in the **live** realm for each environment.
- [ ] Run the end-to-end smoke in each deployed environment: request → link
  email (correct per-app host) → `send-code` → code email → `verify-code` →
  usable session. Record the HTTP status of each hop; `503` on the OTP hop means
  the corresponding prerequisite is still missing — name the ticket in the
  failure, do not re-run blindly.
- [ ] Update `docs/ENV_VARS.md` (docs repo) with the observed per-environment
  matrix, and record in the release/PR notes that **Phase 9 is not verified in a
  deployed environment** until this matrix is green.
- [ ] Report the outcome to the team lead so `PAIML-KEYCLOAK-024` (QA) and
  `PAIML-KEYCLOAK-025` (FUTURE) can be scheduled or held accordingly.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] The matrix is complete and **green for dev, staging and prod** — every
  requirement observed live in every deployed environment, no row left "should
  be fine" or inferred from the repo.
- [ ] Each row cites how it was observed (live Secret key list / ConfigMap read /
  Admin API read), with secrets redacted in the evidence.
- [ ] `FE_BASE_URL` / `ANALYST_BASE_URL` match the per-environment table in
  028 — explicitly confirmed that prod is **not** on the demo duckdns hosts.
- [ ] Full OTP round-trip succeeds in at least one **deployed** environment
  (all three preferred), with per-hop status codes recorded.
- [ ] `docs/ENV_VARS.md` updated with the observed matrix; the statement
  "Phase 9 unproven in deployed environments" is **removed** only once the
  matrix is green.
- [ ] Explicit statement recorded that Direct Access Grants stay enabled until
  `PAIML-KEYCLOAK-025` replaces the hidden-password grant.

## Integration Tests to Run (Local Verification)
- [ ] Manifest sweep per environment: pepper + Brevo key in the Secret, absent
  from the ConfigMap; both URLs present in the ConfigMap.
- [ ] Live realm Admin API read per environment (tokens redacted) asserting
  `directAccessGrantsEnabled == true` on both app clients.
- [ ] Deployed E2E smoke per environment with per-hop status codes; a `503` is
  reported as a named missing prerequisite, not a generic failure.
- [ ] Regression guard: confirm the failure mode is still fail-closed — clearing
  the pepper in a scratch environment returns 503 rather than serving a
  code hashed without one (proves the gate is testing a real control).

## Dependencies
- **Blocks:** None (terminal gate for this phase; unblocks a deployed-environment
  claim for `PAIML-KEYCLOAK-024` and the scheduling of `PAIML-KEYCLOAK-025`)
- **Blocked By:** PAIML-KEYCLOAK-026, PAIML-KEYCLOAK-027, PAIML-KEYCLOAK-028

## Estimated Effort
- [M] (Medium 3–5h)
