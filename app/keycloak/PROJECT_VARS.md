# Project Variables: keycloak

## Ticket Counter
- **Last ticket number**: 33

> Anomaly note (docs-unified): incoming `docs/PAIML-POLE-FE-013-logout` counter was 14 (older, phases 5-6 only); superseded, MAX 20 kept (phases 7-8 present).

> 026–029 = **Phase 10** (`phase-10-otp-deploy-prerequisites`) — the INFRA
> (`pole-ai-ml-infra`) tickets that own the DEPLOY prerequisite for the Phase 9
> passwordless flow. Authored in the docs repo only; the code-side infra PRs are
> scheduled separately by the team lead.

> 030–031 = **Phase 11** (`phase-11-qa-gate-fixes`) — the QA-gate fixes for Phase 9.

> 032–033 = **Phase 12** (`phase-12-two-step-otp`) — Two-Step Temporary Access
> **UX hardening**, not a build phase. The `send-code` / `verify-code` backend,
> the 10-min TTL, single-use, prior-code invalidation, the 5-attempt cap and the
> 60s resend cooldown already exist from Phase 9 (PAIML-KEYCLOAK-021..022), as
> do the `/activate` pages, `ActivationFlow` and `activation-core.ts` in both
> `pole_fe` and `pole_analyst` (PAIML-KEYCLOAK-023). Phase 12 adds only:
> **032** (BE — `send-code` idempotent inside the resend cooldown: `200`
> `already_sent: true` when a live code is armed, 429 preserved) + **033** (FE
> x2 — auto-send on page load, drop the "Validate" gate, "code sent" notice,
> consume the `already_sent` flag).
>
> The original 032–035 draft described work that already exists (BE OTP
> dispatch, per-app verification UIs, and an integration/QA gate); it was
> replaced on 2026-09-28 after the code was read. 034 and 035 were **deleted**,
> not renumbered — the counter therefore ends at **33**.
