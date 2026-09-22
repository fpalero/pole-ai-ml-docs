# Ticket: PAIML-POLE-API-137

## Title
Harness real-session discovery + revert fake seed-measurements endpoint (revert code PR #332; pole-ai-ml repo)

- **Status**: ✅ DONE (merged via code PR #333 → squash `9984851` into develop; local review APPROVED; CI green except one unrelated pre-existing vitest tab-spec flake `analysis-detail.page.spec.ts` 1132/1133 — recorded as observed flake)
- **Project**: pole_api (harness + seed endpoint revert)
- **Phase**: 42 coach-gate-25
- **Blocks**: —
- **Blocked By**: — independent of 134/135/136.

## Context

Phase-42 gate iter-3 USER DECISIONS (binding): (1) **No mock data** — real
performances uploaded via pole_fe by the user on staging (handspring + Shoulder
Mount only). (2) **Revert** ticket 131's fake `seed-measurements` endpoint
(code PR #332) and the DEVOPS-002 staging opt-in (`--set
pole-api.allowSeedMeasurements=1`, infra PR #39 — see DEVOPS-003).
(3) Absence of data is a tested behavior (134 T2/T3), not a setup failure.

Ticket 131 (✅ DONE, merged via #332 → `3a335cf`) is therefore superseded: the
fake-seed approach is rejected, the endpoint must go.

## Scope

(a) **REVERT code PR #332 cleanly** (pole-ai-ml repo):

- Remove `POST /api/analysis/videos/{id}/seed-measurements`,
  `submit_seed_measurements` / `_run_seed` / `_seed_allowed`, `ForbiddenError`
  (keep only if used elsewhere — verify), `Settings.allow_seed_measurements`,
  and its tests.
- Keep the incidental `_FakeJobRunner` fidelity fix ONLY if it repairs a test
  failing on develop without the endpoint (verify, else revert it too).

(b) **E2E harness real-session discovery** (`seedCoachedVideo` / `ensureScored`):

- FIND-OR-USE real user-uploaded coached sessions by trick-label convention —
  define it (only handspring + Shoulder Mount initially) — instead of uploading
  the 0-frame mirror fixture.
- DELETE the fake-seed fallback path.
- Until footage exists, setup fails fast with "missing real session for
  \<trick\>" (not silent fakes).

## Validation Plan
1. `rg "seed-measurements|seed_measurements|allow_seed|allowSeedMeasurements|_seed_allowed" app/`
   → zero hits (app + harness).
2. Harness dry-run: lists required real sessions per trick; fails fast with
   "missing real session for \<trick\>" when footage is absent.
3. With real handspring/Shoulder Mount footage on staging: readiness setup
   finds and uses the real sessions (no upload of the mirror fixture, no
   fake-seed call).

## Acceptance Criteria
- [x] Zero references to `seed-measurements` / forced-fake seeding in app +
      harness (verified: zero `seed-measurements|seed_measurements|allow_seed|_seed_allowed` hits in app).
- [x] PR #332 revert verified item-by-item (endpoint, helpers, setting, error
      class conditional, tests) — `ForbiddenError` + test file deletion
      reverted; `_FakeJobRunner` fidelity fix KEPT with develop-failure proof.
- [x] Harness lists required real sessions per trick (handspring + Shoulder
      Mount convention defined via find-or-use real sessions
      `REAL_SESSION_TRICKS=['handspring','shoulder-mount']`); fail-fast message exact:
      "missing real session for \<trick\>".
- [x] No mock/fixture upload path remains in `seedCoachedVideo`/`ensureScored`.

## Dependencies
- **Blocked By**: — (pairs with DEVOPS-003 infra revert; neither blocks the
  other).
- **Blocks**: —.

## Estimated Effort
- [M]
