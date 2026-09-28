# Project Variables: keycloak

## Ticket Counter
- **Last ticket number**: 35

> Anomaly note (docs-unified): incoming `docs/PAIML-POLE-FE-013-logout` counter was 14 (older, phases 5-6 only); superseded, MAX 20 kept (phases 7-8 present).

> 026–029 = **Phase 10** (`phase-10-otp-deploy-prerequisites`) — the INFRA
> (`pole-ai-ml-infra`) tickets that own the DEPLOY prerequisite for the Phase 9
> passwordless flow. Authored in the docs repo only; the code-side infra PRs are
> scheduled separately by the team lead.

> 030–031 = **Phase 11** (`phase-11-qa-gate-fixes`) — the QA-gate fixes for Phase 9.

> 032–035 = **Phase 12** (`phase-12-two-step-otp`) — Two-Step Temporary Access
> **UX hardening** plus the temp-access product decisions, not a build phase. The
> `send-code` / `verify-code` backend, the 10-min TTL, single-use, prior-code
> invalidation, the 5-attempt cap and the 60s resend cooldown already exist from
> Phase 9 (PAIML-KEYCLOAK-021..022), as do the `/activate` pages, `ActivationFlow`
> and `activation-core.ts` in both `pole_fe` and `pole_analyst`
> (PAIML-KEYCLOAK-023). Phase 12 adds:
> - **032** (BE — `send-code` idempotent inside the resend cooldown: `200`
>   `already_sent: true` when a live code is armed, 429 preserved)
> - **033** (FE ×2 — auto-send on page load, drop the "Validate" gate, "code sent"
>   notice, consume the `already_sent` flag)
> - **034** (FE ×2 — **Q2**: explain the 14-day cooldown in EN/ES on `/activate`;
>   a distinct cooldown state for the existing `409`, plus the existing `410`
>   `expired-link` / `404 invalid-link` states. **Presentation only — no backend
>   change is spec'd**; the 409 + `Retry-After` already exists)
> - **035** (BE — **Q3**: durable MongoDB `temp_access_audit` ledger — `email`,
>   `app`, `link_issued_at`, `window_started_at`, `use_count`, `consumed_tokens` —
>   written at link-issue and window-start, **never deleted by the purge**,
>   idempotent on re-entry, and **additive only** so the 14-day `temp:req` marker
>   stays the cooldown's source of truth (PAIML-KEYCLOAK-031). Retention/pruning is
>   **deferred**)
>
> **Q1 (magic-link re-use) required NO code change.** Per
> [ADR-007](../../decisions/ADR-007-temp-access-link-reuse-and-audit-retention.md)
> (user-confirmed 2026-09-27): the link **may** be re-used, but **only while the 2h
> window is live**; once the 2h lapses the link is dead and the user must wait out
> the 14-day cooldown and request a brand-new one. That is the already-shipped
> behaviour, recorded **as a decision record only** so a future reader does not
> "fix" it.
>
> **Numbering history:** the original 032–035 draft described work that already
> exists (BE OTP dispatch, per-app verification UIs, an integration/QA gate); it
> was replaced on 2026-09-28 after the code was read, and its 034/035 were
> **deleted, not renumbered**. The numbers were **re-issued the same day** for the
> Q2/Q3 work above, hence the counter ending at **35**.
>
> **Graph:** `032 → 033 → 034` and `032 → 035` — acyclic, every `Blocked By`
> symmetric with the other ticket's `Blocks`.
