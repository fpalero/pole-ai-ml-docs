# Plan Phase 10 — OTP Deploy Prerequisites (infra repo `pole-ai-ml-infra`)

> **Parent plan:** [PLAN.md](../PLAN.md)
> **Status:** 📋 PLANNED — tickets 026–029 authored in the docs repo; **no infra code changed yet**. The code-side PRs are scheduled separately by the team lead.
> **Class:** INFRA only (repo `pole-ai-ml-infra`, remote `git@github.com:fpalero/pole-ai-ml-infra.git`, mainline `develop` + user-owned `main`). **No `pole-ai-ml` changes.** Chart paths below are relative to the **infra repo root** (on disk: `infrastracture/`).
> **Why this phase exists:** Phase 9 shipped the passwordless link+OTP flow in `pole-ai-ml`, but the values it needs in a *deployed* environment are not provisioned anywhere. The `PAIML-KEYCLOAK-024` QA gate is running **locally** (values provisioned in the local stack), so a green local run proves the code path and **nothing** about dev/staging/prod.

## Scope

Own the **DEPLOY prerequisite** for the Phase 9 passwordless temp-access flow.
The code is done and locally exercised; this phase makes the flow actually
*reachable* in a deployed environment, and makes that provable.

Four provisioning gaps, surfaced during `PAIML-KEYCLOAK-021/022` implementation
and recorded in [`docs/ENV_VARS.md`](../../../ENV_VARS.md):

| # | Gap | Failure mode when missing | Placement | Ticket |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `TEMP_ACCESS_OTP_PEPPER` | `send-code` / `verify-code` answer **503** (fail-closed) | `pole-api` **Secret** | 026 |
| 2 | Direct Access Grants on `pole-fe` + `pole-analyst` | hidden-password session grant rejected | keycloak realm | 027 |
| 3 | `FE_BASE_URL` / `ANALYST_BASE_URL` | temp-token app binding missing; links point at the wrong host | `pole-api` **ConfigMap** | 028 |
| 4 | `BREVO_API_KEY` | request endpoint answers **503** | `pole-api` **Secret** | 028 |

Plus the rollout gate (029) that keeps a *local* green from being reported as a
*deployed* one.

## Verified starting state (read 2026-09-26, local cluster `k3s-local`)

Recorded so the tickets are not guesses, and so a future reader can tell what
changed:

- **`pole-api` live ConfigMap carries only** `TEMP_ACCESS_COOLDOWN_S`,
  `TEMP_ACCESS_WINDOW_S`, `TEMP_ACCESS_TOKEN_TTL_S`,
  `TEMP_ACCESS_SWEEPER_INTERVAL_S`. `TEMP_ACCESS_OTP_PEPPER`, `FE_BASE_URL`,
  `ANALYST_BASE_URL`, `BREVO_API_KEY` (and the OTP tunables `OTP_TTL_S`,
  `OTP_MAX_ATTEMPTS`, `OTP_RESEND_COOLDOWN_S`) are **absent**.
- **`pole-api` live Secret keys:** `API_KEY`, `KEYCLOAK_ADMIN_CLIENT_SECRET`,
  `MONGODB_URI`, `OPENROUTER_API_KEY` — no OTP pepper, no Brevo key.
- **Direct Access Grants are already `true`** on `pole-fe` and `pole-analyst` in
  **both** declarative sources (chart ConfigMap embedded realm and
  `keycloak/realm-pole-ai.json`) **and** in the live local realm (Admin API).
  → Gap 2 is therefore a **verification + drift-repair** ticket, not a blind
  config flip. See 027.
- **Repo-wide grep finds no** `TEMP_ACCESS_OTP_PEPPER` / `FE_BASE_URL` /
  `ANALYST_BASE_URL` / `BREVO_API_KEY` in any infra yaml/workflow/script — the
  values have never been wired.
- **Secret injection pattern to follow:** `--set pole-api.<key>=${{ secrets.<NAME> }}`
  in `.github/workflows/deploy-{dev,prod}.yml` (as done for
  `openrouterApiKey` / `keycloakAdminClientSecret`).

## Chart / file map (paths relative to the **infra repo root**)

| Path | Role in this phase |
| :--- | :--- |
| `helm/pole-ai/values.yaml` | chart values (`pole-api` block); placeholders only, no real secrets |
| `helm/pole-ai/values-local.yaml` / `values-dev.yaml` | per-environment overrides |
| `helm/pole-ai/charts/pole-api/templates/configmap.yaml` | `FE_BASE_URL`, `ANALYST_BASE_URL` land **here** |
| `helm/pole-ai/charts/pole-api/templates/secret.yaml` | `TEMP_ACCESS_OTP_PEPPER`, `BREVO_API_KEY` land **here** |
| `helm/pole-ai/charts/pole-api/templates/deployment.yaml` | consumes ConfigMap + Secret; rollout trigger check |
| `helm/pole-ai/charts/keycloak/templates/configmap.yaml` | embedded realm — `directAccessGrantsEnabled` (already `true`) |
| `keycloak/realm-pole-ai.json` | standalone realm source — must agree with the chart |
| `helm/pole-ai/charts/keycloak/files/realm_sync.py` | `partialImport` `policy: OVERWRITE` — why a console-only fix does not stick |
| `.github/workflows/deploy-dev.yml`, `deploy-prod.yml` | secret injection via Actions secrets |

## Tasks

### Ticket 026 — `TEMP_ACCESS_OTP_PEPPER` as a Helm Secret (per environment)

- [ ] [Infra] `tempAccessOtpPepper` value (placeholder default) + render
  `TEMP_ACCESS_OTP_PEPPER` into the `pole-api` **Secret**, never the ConfigMap,
  never a committed real value; inject per environment via
  `--set pole-api.tempAccessOtpPepper=${{ secrets.TEMP_ACCESS_OTP_PEPPER }}`.
- [ ] [Infra] Confirm pod restart picks the Secret env up (Secret env changes do
  not trigger a ConfigMap-style rollout on their own).
- [ ] Full details in `phase-10-otp-deploy-prerequisites/PAIML-KEYCLOAK-026.md`.

### Ticket 027 — Direct Access Grants: verify live, repair declaratively

- [ ] [Infra] Read `directAccessGrantsEnabled` per environment via the Admin
  API (repo state is **not** evidence of live state); repair declaratively if an
  environment drifted; reconcile the two realm sources; keep the grant enabled
  until ticket 025 replaces the hidden-password mechanism.
- [ ] Full details in `phase-10-otp-deploy-prerequisites/PAIML-KEYCLOAK-027.md`.

### Ticket 028 — `FE_BASE_URL` / `ANALYST_BASE_URL` + `BREVO_API_KEY`

- [ ] [Infra] Host map into the `pole-api` **ConfigMap**; Brevo key into the
  **Secret**; per-environment values (demo/staging duckdns hosts, local
  `localhost:4200`/`4300`, prod explicit — never inheriting the demo hosts).
- [ ] Full details in `phase-10-otp-deploy-prerequisites/PAIML-KEYCLOAK-028.md`.

### Ticket 029 — Deployed-environment prerequisite matrix (rollout gate)

- [ ] [Infra] Per-environment matrix over dev/staging/prod with **observed**
  (not inferred) state; deployed OTP round-trip smoke; update
  `docs/ENV_VARS.md`; report to the team lead.
- [ ] Full details in `phase-10-otp-deploy-prerequisites/PAIML-KEYCLOAK-029.md`.

## Decisions (this phase)

1. **Secrets vs ConfigMap.** `TEMP_ACCESS_OTP_PEPPER` and `BREVO_API_KEY` are
   **Secrets** (they are credentials, and the pepper's whole purpose is to make
   an offline OTP brute-force infeasible). `FE_BASE_URL` and `ANALYST_BASE_URL`
   are **ConfigMap** values: a public origin is not a secret, and it must be
   visible/auditable in `kubectl get cm` and editable per environment without
   touching a secret store.
2. **No hardcoded secrets, ever.** `values.yaml` carries **placeholders only**,
   following the existing `keycloakAdminClientSecret:
   "admin-secret-placeholder"` pattern. A committed pepper is a broken pepper:
   the fail-closed 503 is a feature.
3. **Per-environment peppers.** Not shared across environments — a shared pepper
   would let a code captured in one environment validate against another's
   `temp:code` hash.
4. **Host map is security config, not cosmetics.** `FE_BASE_URL` /
   `ANALYST_BASE_URL` are the temp-token app binding *and* the `Origin`
   resolution source for `send-code` / `verify-code`; a wrong value fails
   *quietly* (real users get a link to the wrong app), so the per-environment
   values are acceptance criteria, not comments.
5. **The deployed environment is unproven until these land.** A green local
   `PAIML-KEYCLOAK-024` proves the code path only. "Phase 9 works" is not a
   claim anyone may make from a local run; 029 is the artifact that changes it.
6. **No `main` PRs, ever.** This phase's PRs target `develop` in
   `pole-ai-ml-infra`; `develop` → `main` is a user-owned manual release.

## Dependencies

- Ticket order: 026, 027, 028 are independent; 029 blocks on all three.
- **Blocked by (upstream, already done):** `PAIML-KEYCLOAK-021` (host map +
  Brevo carry-overs), `PAIML-KEYCLOAK-022` (OTP pepper + DAG).
- **Blocks:** a deployed-environment claim for `PAIML-KEYCLOAK-024` (QA gate);
  scheduling of `PAIML-KEYCLOAK-025` (FUTURE token exchange — which also
  eventually lets Direct Access Grants be turned back **off**).
- Existing infra mechanisms reused: `realm-sync` Job (`PAIML-INFRA-036/037`),
  the Actions `--set` secret pattern, the FE/analyst env-ConfigMap rollout
  trigger (`PAIML-INFRA-035`).

## Acceptance Criteria

- [ ] All four provisioning gaps are closed in dev, staging and prod, each
      **observed live** (not inferred from the repo).
- [ ] No real secret value is committed in the infra repo; the pepper and Brevo
      key exist only as Actions secrets and rendered Secret data.
- [ ] Deployed E2E: request → per-app link email (correct host) → `send-code` →
      code email → `verify-code` → usable session, in at least one deployed
      environment (all three preferred).
- [ ] Fail-closed behaviour still holds where a prerequisite is missing (503,
      not a served code hashed without a pepper).
- [ ] Direct Access Grants remain enabled with the 025 follow-up recorded.
- [ ] `docs/ENV_VARS.md` reflects the observed per-environment matrix.

## Risks and Mitigations

- **Risk: a green local `PAIML-KEYCLOAK-024` is reported as "Phase 9 works".**
  **Mitigation:** 029 makes the deployed matrix the signed-off artifact; the
  plan/ENV_VARS wording states the local run proves the code path only.
- **Risk: per-environment drift** (right in staging, missing in prod).
  **Mitigation:** 029 checks each environment separately and records how each
  row was observed; 028's per-environment table makes drift visible.
- **Risk: a console-only realm fix is reverted** by the next `realm-sync`
  (`policy: OVERWRITE`). **Mitigation:** 027 mandates the fix lands in the
  declarative sources and is re-read *after* a realm-sync re-run.
- **Risk: wrong host map fails quietly** (link to the wrong app).
  **Mitigation:** acceptance criteria assert the host in the *emailed link*,
  not just the value in the ConfigMap.
- **Risk: secret injection lands in a log.** **Mitigation:** follow the
  existing `--set` pattern; verify the rendered value never appears in workflow
  output.
