# Keycloak temporary-user auto-expiry — design note

> **Type:** Explanation + rollout runbook for operators.
> **Status:** Accepted for implementation (user-approved 2026-09-07, 30-minute check interval).
> **Decision record:** `docs/decisions/ADR-005-keycloak-temp-user-expiry-cronjob.md` (the *why*).
> **Implementation home:** `pole-ai-ml-infra` repo (K8s CronJob + script); this note is the contract the infra implementation must honor.
> **Date:** 2026-09-07.

## 1. Problem + decision

**Problem.** Temporary Keycloak accounts linger `enabled` until a human disables
them by hand. Staging evidence (2026-09-07, `pole-ai` realm): the temp account
`fpalero1986@gmail.com` was still `enabled` past its useful life with only
`fe-user` + defaults roles (no `analyst-user`, so its actions were already
role-blocked) — yet nothing would ever have disabled it without the team-lead's
manual `PUT enabled=false` + session kill. Keycloak 26 has **no native
account-expiry**, and the existing `pole_api` enforcement (Redis `temp:*`
markers, 2h window, lazy purge + sweeper — see `docs/app/keycloak/`,
phase 8 `PAIML-KEYCLOAK-018…020`) only sees users it created markers for. If the
markers are absent or Redis state is lost, the realm account stays live
indefinitely: a gap only a Keycloak-side mechanism can close.

**Decision.** A dedicated **Kubernetes CronJob in the `pole-ai-ml-infra` repo**,
schedule **`*/30 * * * *`**, that disables past-due temp users directly against
the Keycloak Admin API.

**Why NOT an in-app scheduler in `pole_api`** (see ADR-005): every `pole_api`
replica would need privileged Keycloak credentials to disable users. That fans
out a highly-privileged secret to all API pods and couples realm hygiene to API
uptime/scale. A CronJob runs one short-lived pod per tick under its own
ServiceAccount-less identity with a single-purpose client, isolating the
`manage-users` privilege from the serving path entirely.

## 2. Expiry contract

- At account creation (temp-access enrollment), set a custom Keycloak user
  attribute **`account_expires_at`** holding the expiry instant in **ISO-8601
  UTC** (e.g. `2026-09-07T12:00:00Z`).
- The job disables a user **iff** `account_expires_at` is present, parses as a
  past instant (modulo the §6 grace margin), **and** the user is still
  `enabled`.
- **Safety invariant (explicit): users WITHOUT the `account_expires_at`
  attribute are NEVER touched.** Ordinary permanent accounts carry no such
  attribute, so a bug in time comparison or paging can at worst affect temp
  users, never the regular user base. The setter (enrollment path) and the
  reader (CronJob) must agree on the attribute name exactly; any rename is a
  coordinated change to both sides.

## 3. Service account (least privilege)

- Dedicated **confidential client** in the `pole-ai` realm created for this job
  only (e.g. `temp-user-expiry`), **service-accounts-enabled**, with **only**
  the `realm-management → manage-users` role. No `view-realm` beyond what
  listing users needs (covered by `manage-users`), no admin-console access.
- The client secret lives in a **Kubernetes Secret created by the operator via
  `kubectl`** (`kubectl create secret generic … --from-literal=…`). It is
  **never committed** to any repo (not `pole-ai-ml-infra`, not docs).
- The job script authenticates with the **client-credentials grant** against the
  realm token endpoint, mints a fresh token each run (no token persistence),
  and passes it as a Bearer token to the Admin API.

## 4. Job flow

Each tick the (short-lived) job pod runs:

1. **Mint token** — client-credentials grant → access token in memory.
2. **Page `GET /admin/realms/pole-ai/users`** — iterate all pages (`first`/`max`
   pagination; never assume a single page) and select users where
   `account_expires_at` exists, parses, is past-due (with grace, §6), **and**
   `enabled == true`.
3. For each match, in order:
   - `PUT /admin/realms/pole-ai/users/{id}` with `{"enabled": false}`;
   - `DELETE /admin/realms/pole-ai/users/{id}/sessions` (kill live sessions so
     already-issued tokens stop working at next validation);
   - **log one line to stdout per action** (who, what, when) — pod logs are the
     audit trail (`kubectl logs job/…`).
4. **`DRY_RUN=true` env support (log-only):** when set, the job performs steps
   1–2 and logs exactly what it *would* disable, but issues no `PUT`/`DELETE`.
   Dry-run is the default for first deploy (§5).

## 5. Rollout (dry-run first) + live-test plan

1. Deploy the CronJob with **`DRY_RUN=true`**; let 2–3 ticks run; inspect
   `kubectl logs` — expect "would-disable" lines only, no mutations.
2. Flip to enforce (`DRY_RUN=false`, or remove the env) once the dry-run output
   matches expectations.
3. **Live test on staging:**
   - create a throwaway temp user carrying `account_expires_at` set in the
     past;
   - trigger immediately with `kubectl create job --from=cronjob/<name> …`
     (no waiting for the schedule);
   - verify the user is `enabled=false` **and** its sessions are gone;
   - delete the throwaway user.
4. Keep one dry-run-capable toggle permanently: any future expiry-logic change
   re-rolls out via dry-run first.

## 6. Risks / mitigations

| Risk | Mitigation |
| :--- | :--- |
| **Clock skew** between job pod and Keycloak (user disabled seconds early/late) | Compare against server time; apply a **5-minute grace margin** — only disable when `now > expires_at + 5 min`. |
| **Runaway disable** (bug disables the wrong users) | Attribute-absent = untouched (§2 invariant); ship dry-run first (§5); every action stdout-logged for audit (§4). Blast radius is bounded to temp users by construction. |
| **Secret rotation** (client secret leaks or expires) | Rotate in Keycloak admin console → update the K8s Secret via `kubectl` → delete completed job pods so the next tick picks it up. No repo change, no image rebuild, no API restart involved. |
| **Paging miss** (large realm, single-page listing) | Always paginate `first`/`max` to exhaustion; log the scanned-user count per tick so a silently-truncated scan is visible. |
| **Attribute format drift** (non-ISO value set by a future enrollment change) | Treat unparsable values as "not past-due, loudly": skip the user and log a warning. Never disable on a value you cannot parse. |

## 7. Index / cross-references (deliberate no-touch)

- `docs/dev-ops/PLAN.md` is the CI/CD implementation plan; this CronJob is
  runtime infra hygiene, not CI — intentionally **not** added there (no bloat).
- `docs/index.md` maps project → `PLAN.md` only; no per-note index entry exists
  by convention, so none was added.
- Related prior art: `docs/app/keycloak/` phases 2 + 8 (app-side temp-access
  orchestration, lazy purge, sweeper observability) and the `pole-api-admin`
  client (`PAIML-KEYCLOAK-002`). This job is the Keycloak-native safety net
  underneath those layers, not a replacement.
