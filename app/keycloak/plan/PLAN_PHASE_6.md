# Plan Phase 6 — Stitch Pixel-Perfect Login Restyle

> **Parent plan:** [PLAN.md](../PLAN.md)
> **Status:** ✅ DONE (implementation + QA GREEN; awaiting USER manual
> develop→main promotion — NOT closed until the user confirms)

> **Note:** no Phase 6 doc existed in the docs repo; this file is a minimal
> merge record reconstructed from the team-lead handover (infra PR #24 +
> Tester QA gate). Scope below states only handover facts — nothing invented.

## Scope

Restyle the `pole-ai-login` Keycloak theme pixel-perfect to the Stitch design
(desktop + mobile), keeping the Phase 2 temp-access POST behavior intact.

## Merge record

- Infra PR [#24](https://github.com/fpalero/pole-ai-ml-infra/pull/24) —
  MERGED (squash `b04bb69` into `develop`).
- Ticket: `phase-6-stitch-login-restyle/PAIML-KEYCLOAK-014.md`.
- fe-developer conformance verdict: PIXEL-PERFECT, no fix PR.

## QA gate result

- **Verdict:** GREEN, 4/4 (Tester phase-end gate, local k3s rev 13). Error list empty.
- **Checks:** (1) visual desktop+mobile; (2) password POST failure-path;
  (3) magic-link 202/Mailpit + 422 + 409; (4) en render + es key parity.
- **Evidence:** `/tmp/qa014-*`.
- **Non-blocking observations:**
  1. Realm i18n flag off locally (es fallback; theme parity proven).
  2. Theme fetch uses relative `/api/auth/temporary-access` with
     `data-endpoint` override (pre-existing Phase 2 behavior).
- **Promotion pending:** USER manual testing + manual develop→main promotion.

## Dependencies

- Phase 1: `pole-ai-login` custom login theme.

## Acceptance Criteria

- [x] Theme matches the Stitch design (fe-developer PIXEL-PERFECT).
- [x] Phase-end QA gate GREEN (4/4).
- [ ] USER manual testing + manual develop→main promotion (open).
