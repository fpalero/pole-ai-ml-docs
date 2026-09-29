# ADR-007: Temporary-access link reuse, cooldown UX, and audit retention

> Repo-wide architectural decision record for the **temporary-access** (magic
> link + 2h window + 14-day cooldown) flow. Applies to `pole_api`
> (`app/pole_api/src/core/temp_access.py`, `auth/controllers/temporary_access.py`,
> `core/auth.py`, `core/temp_access_purge.py`) and the `/activate` pages in
> `pole_fe` / `pole_analyst`. Project plans: `docs/app/keycloak/PLAN.md`,
> `docs/app/keycloak/plan/PLAN_PHASE_12.md`.

## Status
Accepted

## Date
2026-09-27 (questions confirmed by the user; recorded 2026-09-28)

## Context

The temporary-access flow lets an anonymous visitor get 2 hours of access to
`pole_fe` / `pole_analyst` by supplying only an email. Three product questions
came out of a review of that flow, and each has a **different** correct answer.
Recording them here — and only here — because the current code is easy to
misread as a bug:

- **Q1 — link reuse.** The direct link lives 24h (`temp:token:{token}`, TTL
  `TEMP_ACCESS_TOKEN_TTL_S`) and the activated access window is 2h
  (`temp:active:{email}:{app}`, `ts_end = ts_start + 2h`, **never extended**).
  A reader can reasonably conclude that a 24h link is meant to be re-openable
  and that the 2h cap is a bug to be fixed, or that the 2h cap means the link
  is single-use. Neither conclusion is right, and the code has no comment
  saying so.

- **Q2 — cooldown UX.** The 14-day cooldown is enforced by a
  `SETNX` on `temp:req:{email}:{app}` with a 14-day TTL
  (`TEMP_ACCESS_COOLDOWN_S`, default `14 * 24 * 3600`). Today a repeat request
  from the same email inside that window answers
  **HTTP 409** with a bare detail string — e.g.
  `{"detail":"Email in cooldown — try again in 336 hours"}` — plus a
  `Retry-After` header in seconds. The `/activate` page has **no cooldown
  state at all**; nothing in `pole_fe` or `pole_analyst` renders an
  explanation, because the cooldown is raised on the *request* endpoint, and
  the request endpoint is not reachable from the activation page flow once a
  link exists.

- **Q3 — data lifecycle and audit.** The purge service
  (`core/temp_access_purge.py`) physically deletes everything a temp user owns
  (Mongo rows, PVC videos, Chroma vectors, chatbot sessions) and then clears
  the Redis `temp:*` markers. It preserves the 14-day `temp:req` cooldown
  marker (PAIML-KEYCLOAK-031) but keeps **no durable record of who the user
  was or what they did**. That is correct for owned data, but it means a
  user who lapsed and was purged is invisible afterwards: you cannot answer
  "did this person ever use temp access?", "how many times?", or "is this
  token the one they already burned?".

---

## Decision 1 (Q1) — Link re-use is allowed, but only while the 2-hour window is live

**The magic link MAY be re-used, but only while the 2-hour window is live.**
Once the 2h window lapses, **the link is dead**: the user must wait out the
14-day cooldown and request a **brand-new** link. The old one is not revived,
re-issued or extended — the only recovery path is a new request after the
cooldown.

This is **the currently shipped behaviour** and it is **not a defect**:

- the `temp:token:{token}` record lives 24h, which is a *lifetime*, not a
  promise of re-usability;
- `start_window` writes the window with `SET … nx=True` and pins
  `ts_end = ts_start + window`. It is idempotent by design
  (PAIML-KEYCLOAK-022): the first writer decides, later re-entries confirm,
  and **nothing can push `ts_end` forward**. A re-used link therefore does not
  extend access;
- once the window has lapsed, `_enforce_temp_access_window`
  (`core/auth.py`) rejects the request with **403 `TEMP_ACCESS_EXPIRED`** and
  fires a lazy purge that disables the Keycloak user and deletes their data.

**No code change is required or planned for Q1.** The reason this ADR exists is
to stop a future reader — human or agent — from "fixing" this. The pinned rule
is *10:00 → 12:00 stays 12:00*: re-opening a link inside the window must never
move the end, and a lapsed window must never be re-armed by a stale link.

### Consequences

- The 24h token TTL and the 2h window are **two different clocks** and must
  stay decoupled. Shortening the token TTL to 2h would be a behaviour change,
  not a cleanup.
- The "request a new link" affordance on a lapsed link is the **only**
  recovery path, and today it is copy-only (`errorActions['expired-link']` →
  "Request a new link") with no FE endpoint behind it. That gap is real and is
  tracked separately (Q2, PAIML-KEYCLOAK-034), but it does **not** make the
  lapsed-link behaviour wrong.
- Anyone adding a "resume session" feature must not re-arm a lapsed window
  from a stored link; the ledger below records *that the window existed and
  ended*, not a way to reopen it.

---

## Decision 2 (Q2) — The 14-day cooldown stays hard; the application must explain it

**The 14-day cooldown remains a hard wall — the user waits it out.** The
change is to the **presentation**: the application **must** show an
*explanatory message*, not a bare number.

Today the cooldown surfaces only as
`409 {"detail":"Email in cooldown — try again in 336 hours"}` from
`POST /api/auth/temporary-access`, and the `/activate` page has **no cooldown
state at all**. "336 hours" tells the user nothing about *why* they are being
refused or *what to do next*. The copy must explain the situation — the user
already had a session, they can request again after 14 days — in **EN and ES**.

Backend mapping the frontend must render (all of these already exist; this is
presentation only):

| Backend answer | Meaning | FE obligation |
| :--- | :--- | :--- |
| `409` + `Retry-After` | 14-day cooldown active | Render the explanatory cooldown state. Prefer the **re-request date** derived from `Retry-After` over a raw hours number. |
| `410` "Access link has expired" | 24h link TTL lapsed | Existing `expired-link` copy; must not claim the user can re-request immediately. |
| `404` | link unknown / already used / purged | Existing `invalid-link` copy. |

### Consequences

- The backend **already** returns `409` with `Retry-After`; no backend change
  is spec'd. A reader looking for a "cooldown endpoint" will not find one and
  should not add one — the request endpoint is the answer source.
- The `/activate` page gains a **distinct cooldown state** (a new
  `ActivationErrorKind`), which is a type-level change to the shared
  `activation-core.ts` in **both** `pole_fe` and `pole_analyst`, plus the
  mirrored specs (`activation-parity.spec.ts` compares them byte-for-byte).
- The raw backend `detail` string must **not** be rendered — it is English
  only, and the flow ships EN + ES. The FE derives its own copy.
- Work: **PAIML-KEYCLOAK-034** (FE ×2).

---

## Decision 3 (Q3) — Owned data is physically deleted; a durable per-user audit trail is retained forever

Two halves, and they must not be conflated.

**(a) Owned data is physically deleted on purge — unchanged.** Videos, Mongo
rows and Chroma vectors belonging to a temp user are removed outright by the
purge service. This is existing behaviour and is not modified by this ADR.
There is **no** soft-delete, tombstone or anonymisation pass over owned data:
retention of the *data* would defeat the purpose of the purge (temp users must
not leave content that can corrupt shared state), and a soft delete would just
move the storage problem.

**(b) A durable per-user audit trail is retained — and is never deleted by the
purge.** The purge's job is to remove what the user *produced*; it must not
remove the record that the user *existed*. The ledger retains, per user:

| Field | Purpose |
| :--- | :--- |
| the email | who the user was |
| when the magic link was requested (`link_issued_at`) | first contact |
| when the 2h window started (`window_started_at`) | when access actually began |
| a **use counter** (`use_count`) | how many times the link/code flow was used |
| the expired/consumed **token identifiers** (`consumed_tokens`) | so a spent or expired token can be **recognised and never re-used** |

**Retention: forever, for now.** This is an explicit product decision: the app
is a low-traffic demo and the audit trail is the only way to answer "who used
temp access and how often" after the data itself is gone. Permanent retention
is a deliberate choice, not an oversight.

### Consequences

- The ledger lives in `pole_api` in **MongoDB**, is written at **link-issue**
  and **window-start**, and is **additive**: the purge path must never delete
  it, and it must never become the cooldown's source of truth (see below).
- **`consumed_tokens` is a security property, not just bookkeeping.** Once a
  token is in the list, it must be recognisable and refused, even after its
  Redis `temp:token:{token}` record has expired or been purged. Storing the
  identifier must not create a replay path — an identifier is not a credential
  and must never be usable to start a window on its own.
- **Idempotency is required.** Re-entry (a refresh, a second `send-code`, a
  re-used link inside the live window) must update counters/timestamps, not
  append duplicate rows or re-issue.
- **The PAIML-KEYCLOAK-031 invariant must hold.** The 14-day `temp:req`
  cooldown marker in Redis is the cooldown's source of truth. The ledger is
  strictly additive and must never be consulted as the cooldown's arbiter;
  using it for that would reintroduce exactly the class of bug 031 fixed.
  Deleting a Redis cooldown marker must not be "fixed" by consulting Mongo.
- **Unbounded growth is accepted for now.** The ledger will grow without a
  prune. That is acceptable at demo traffic and must be revisited before
  production.
- Work: **PAIML-KEYCLOAK-035** (BE) — ✅ **SHIPPED**
  ([pole-ai-ml#363](https://github.com/fpalero/pole-ai-ml/pull/363)).

### Implementation note (PAIML-KEYCLOAK-035, 2026-09-28)

Recorded because three points below read as settled here but landed differently
in the code, and a future reader should find the reasoning rather than re-derive it.

- **The collection is `temp_access_audit` in the app database**, one document per
  `(email, app)` under a **unique** compound index, so the idempotency
  requirement above is structural rather than conventional. A per-token key was
  rejected: the token is a *property* of the row, not its identity, and a
  per-token key would make `use_count` / `window_started_at` unanswerable from
  one read and turn a re-used link into several "users".
- **First-write-wins is `{"$ifNull": ["$f", now]}` inside an
  aggregation-pipeline `update_one`, not `$setOnInsert`/`$min`.** Either writer
  can legitimately create the row (`start_window` is shared by both entry paths),
  and `$setOnInsert` would stamp a phantom `link_issued_at` in one order and
  leave `window_started_at` null forever in the other. A field that was never
  written is `null`, never epoch. `use_count` is a `$add` of 1 per flow step.
- **`consumed_tokens` stores a peppered SHA-256 digest, not the identifier** —
  the "must not create a replay path" requirement above, satisfied the way
  `core/otp.py` already does it, reusing the existing
  `TEMP_ACCESS_OTP_PEPPER`. Capped at **100 per document** (FIFO, trimmed in the
  same server-side expression). Eviction costs *recognition* of the oldest
  identifiers and nothing about access control: nothing in the ledger authorises
  anything, and the window is governed solely by `start_window`'s immutable
  `ts_end`. That per-document cap is the one bound this work added; the
  collection-level retention below is still deferred.
- **The ledger's connection is built lazily, off the event loop, and its failure is
  memoised.** `TempAccessRepository` is constructed on the hot path of every
  authenticated request (`core/auth.py`), so building the sink in its
  `__init__` put a blocking `create_index` on the request's event loop. The
  build therefore happens at the point of use, dispatched with the write, and a
  failure is cached so a Mongo-less host does not retry it per write. This is
  the concrete form of the "never gates the flow" requirement below.
- **`is_token_consumed()` is a recognition helper, not an enforcement one.**
  Nothing refuses a request on its answer — the Redis record and `start_window`
  are the enforcement surfaces — which is what keeps the ledger from becoming a
  grant. Making it an enforcement path would be a security change needing its
  own ADR.

---

## Deferred

- **Retention / pruning policy for the audit ledger — deferred.** Decision 3(b)
  is *retain forever, for now*. No TTL, no archive tier, no scheduled prune is
  in scope of PAIML-KEYCLOAK-035 or any Phase 12 ticket. A production release
  **must** add a retention job (or a documented archive) before real users are
  onboarded; "forever" is a demo posture, not a permanent architectural
  commitment.
- **No soft-delete of owned data** — permanently out of scope while the purge
  semantics stand. Revisiting it is a new ADR, not a ticket tweak.
- **A backend cooldown *message* endpoint** — deferred. The 409 + `Retry-After`
  from the request endpoint remains the single source; the frontend derives
  its copy. Revisit only if the FE genuinely cannot render a good state from
  status + `Retry-After`.
- **Re-arming a lapsed window from a stored link** — explicitly **not** a
  planned feature. Decision 1 forbids it.

## Alternatives Considered

### Q1 — Make the 24h link single-use outright
- Pros: simplest mental model; no re-use path to reason about.
- Cons: changes shipped behaviour with no user complaint behind it; a user who
  re-opens a link in another tab inside their own 2h window would be logged
  out, which is strictly worse UX. The idempotent window already makes re-use
  safe.
- Rejected: the 2h bound is the security property; the link's re-usability is
  not what grants access.

### Q1 — Extend `ts_end` on re-use (sliding window)
- Pros: user-friendly for anyone still working after 2h.
- Cons: **directly contradicts** the pinned non-extend rule and turns a
  forwarded link into indefinite access — the exact exploit
  PAIML-KEYCLOAK-022's `SET … nx=True` exists to prevent.
- Rejected: security regression, not a UX improvement.

### Q2 — Expose a "cooldown status" GET endpoint
- Pros: the FE could pre-empt the 409 and show the state before submitting.
- Cons: a new unauthenticated endpoint leaks "does this email have/has had an
  account" (an account-enumeration oracle), and duplicates state the 409
  already carries.
- Rejected: 409 + `Retry-After` is sufficient and avoids the enumeration
  surface.

### Q2 — Keep the bare number ("try again in 336 hours")
- Pros: zero work.
- Cons: does not explain *why*, invites support contacts, and is the kind of
  raw internal value users should never be shown.
- Rejected: the decision explicitly requires an explanatory message.

### Q3 — Retain the owned data (soft delete) as the audit trail
- Pros: one store, maximum forensic detail.
- Cons: contradicts the product's core promise that temp users leave no shared
  data; unbounded media growth; the purge exists for data-integrity reasons,
  not storage reasons.
- Rejected: a separate, minimal ledger captures the audit need without
  keeping user content.

### Q3 — Retain the audit trail in Redis alongside `temp:req`
- Pros: no new store, same lifecycle as the cooldown.
- Cons: Redis is volatile and TTL-driven; the whole point of the audit trail is
  to **outlive** the 2h window and the 14-day cooldown. Anything with a TTL
  cannot satisfy "retained forever".
- Rejected: MongoDB is the durable store (and is already the owner of the
  deleted data, so a new collection is the smallest possible change).

## Related Work

- `docs/app/keycloak/plan/PLAN_PHASE_12.md` — Phase 12 plan (auto-send
  hardening, cooldown UX, audit ledger).
- PAIML-KEYCLOAK-032 — `send-code` idempotent inside the 60s resend cooldown
  (the **short** cooldown; distinct from the 14-day one).
- PAIML-KEYCLOAK-033 — auto-send the code on page load.
- PAIML-KEYCLOAK-034 — cooldown-expiry message on the activation flow (Q2).
- PAIML-KEYCLOAK-035 — durable `temp_access_audit` ledger (Q3) — ✅ shipped
  (`pole-ai-ml` PR #363).
- PAIML-KEYCLOAK-031 — the purge must preserve the 14-day `temp:req` cooldown
  (the invariant Decision 3(b) must not break).
- ADR-005 — auto-disable expired Keycloak temp users via a K8s CronJob.
