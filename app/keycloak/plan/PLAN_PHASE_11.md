# Plan Phase 11 — Phase 9 QA-Gate Fixes (verify-code grant + purge semantics)

> **Parent plan:** [PLAN.md](../PLAN.md)
> **Status:** 📋 PLANNED
> **Class:** BE (`pole_api`, repo `pole-ai-ml`). Two independent defect fixes; no infra, no FE, no Keycloak realm change.

## Scope

Close the two defects surfaced by the **RED** Phase 9 QA gate
(`PAIML-KEYCLOAK-024`, run 2026-09-26 on `k3s-local`):

1. **`PAIML-KEYCLOAK-030`** — `verify-code` Direct Access Grant fails on a clean
   environment because `create_or_find_user` omits the realm-required
   `firstName` / `lastName`; the same call site also reuses a disabled temp
   account after purge. **BLOCKER** — the flow cannot complete at all.
2. **`PAIML-KEYCLOAK-031`** — the lapse purge deletes the durable 14-day
   `temp:req` cooldown marker (and may not clear the post-022 OTP key
   families). Contradicts PLAN.md **UC-04** and 024's acceptance criterion.

Both block the **re-run of 024**. Neither is a Phase 9 feature change: they
repair guarantees Phase 9 (021/022) claimed to have.

## Context

The gate proved most of the flow — request → link → send-code → verify-code →
session → window, in-app navigation without re-ask, and the pinned
non-extendable window (`ts_end` unchanged on re-entry, 18/18) all **PASS** — but
returned **RED** because:

- **030** breaks the journey on **any** clean environment (the gate only
  completed it behind a local shim).
- **031** breaks the cooldown guarantee after expiry.
- Gates 2 (rate limits), 3 (Phase 8 no-regression UC-06/07/08 + UC-04), and 4
  (`pixi run test` + coverage) were **NOT RUN** before the gate was cut off, so
  the re-run must cover them in full.

**Trusted result note.** An **interim** QA output claimed the re-entry path
*extended* the 2h window. The **final** run did **not** reproduce this:
`ts_end` was byte-identical across re-entry and the pinned 10:00→12:00 case
passed 18/18. The window-extension claim is **not** an open defect and must not
be ticketed. (The untrusted interim output is retained only for traceability.)

## Tickets

### Ticket 030 — verify-code Direct Access Grant (BLOCKER)
- Add realm-required `firstName` / `lastName` to the create payload; preserve
  them on `set_email_verified`.
- Decide and implement re-enable-vs-rotate for reused disabled accounts.
- Add a **live-realm** password-grant integration test (stubbed sequence tests
  cannot prove a grant).

### Ticket 031 — purge semantics
- Preserve `temp:req:{email}:{app}` (residual 14-day TTL) on lapse purge.
- Confirm/ensure all `temp:code:*` + `temp:code-resend:*` are cleared.
- Regression test pinning both, failing against the pre-fix code.

## Dependencies

- Both tickets **block `PAIML-KEYCLOAK-024`** (its re-run); each `Blocked By: None`.
- Independent of each other (different call sites) — can be implemented in
  parallel, but both must be merged before the gate re-runs.
- Does **not** depend on Phase 10 (infra deploy prerequisites). Phase 10 makes
  the flow reachable in a **deployed** environment; Phase 11 makes the **code**
  correct. A green local 024 still means "code works locally", not "Phase 9
  works" — that is ticket 029's job.

## Acceptance Criteria

- [ ] `verify-code` returns `200` with a usable session on a **fresh clean
  environment with no shim**.
- [ ] After lapse purge, `temp:req` survives with residual TTL; all OTP keys
  are cleared.
- [ ] Both regression tests **fail against the pre-fix code**.
- [ ] `pixi run test` green, ≥80% coverage.
- [ ] `PAIML-KEYCLOAK-024` re-run in full (gates 1–4 + FE evidence) is GREEN.

## Risks and Mitigations

- **Risk:** the live-realm grant test needs a real Keycloak in CI, which the
  existing suite deliberately stubs. **Mitigation:** keep the live test in the
  local/integration lane (where the 024 gate runs) and make the stubbed unit
  suite assert the payload includes the name fields; document the lane split.
- **Risk:** preserving `temp:req` accidentally re-arms a cooldown for an email
  that should be free. **Mitigation:** preserve the **residual** TTL, never
  reset to 14d; assert the residual in the regression test.
- **Risk:** a stale disabled account reused on re-request keeps failing even
  after 030. **Mitigation:** 030 explicitly owns the reuse path with a test.
