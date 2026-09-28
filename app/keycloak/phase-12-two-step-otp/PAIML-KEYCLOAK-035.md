# Ticket: PAIML-KEYCLOAK-035

## Title
[Keycloak / pole_api] Durable `temp_access_audit` ledger in MongoDB: retain a per-user audit trail that the purge never deletes

## Description
**Owned data is physically deleted on purge — that is unchanged and correct.**
Videos, Mongo rows, Chroma vectors and chatbot sessions belonging to a temp
user are removed outright by `TempAccessPurgeService.purge()` (reached from
`core/temp_access_purge.py::_full_purge`). **This ticket does not soften that
in any way** — no soft delete, no tombstone, no anonymisation pass over owned
data. See "Explicitly OUT of scope" below.

**The gap this ticket closes.** The purge is *complete*: it deletes the user's
content and clears the Redis `temp:*` markers, keeping only the 14-day
`temp:req:{email}:{app}` cooldown marker (PAIML-KEYCLOAK-031). That means a
lapsed temp user leaves **no durable trace at all**. Nobody can answer:

- which email addresses have ever used temporary access;
- when a link was requested, and when the 2h window actually started;
- how many times a given user went through the link/code flow;
- whether a particular token is one the user already burned.

ADR-007 (Decision 3) splits the two concerns cleanly: the purge removes what
the user *produced*; it must not remove the record that the user *existed*.

**The deliverable.** A durable, per-user **audit ledger** in MongoDB, written at
**link-issue** and **window-start**, holding the fields listed below, and
**never deleted by the purge**. It is **additive**: a new record, in a new
collection, that nothing else reads as a source of truth.

### Fields

| Field | Meaning | Written when |
| :--- | :--- | :--- |
| `email` | the temp user's address | link-issue |
| `app` | the enrollment app (`pole-fe` / `pole-analyst`) | link-issue |
| `link_issued_at` | when the magic link was requested | link-issue |
| `window_started_at` | when the 2h window started | window-start |
| `use_count` | how many times the link/code flow was used | incremented on re-entry |
| `consumed_tokens` | identifiers of spent/expired tokens | when a token is consumed/expires |

`consumed_tokens` is a **security** property, not bookkeeping: a token in that
list must be *recognisable* and **never honoured again**, even after its Redis
`temp:token:{token}` record has expired or been deleted by the purge. Today a
deleted `temp:token:{token}` key and a never-issued token are indistinguishable
(both 404), so a spent token is only "recognised" while Redis still remembers
it.

## The hard constraint — do not reintroduce the PAIML-KEYCLOAK-031 bug

**The 14-day `temp:req:{email}:{app}` Redis marker is, and must remain, the
cooldown's source of truth.** PAIML-KEYCLOAK-031 exists because the lapse
purge was destroying that marker, which let a purged user re-request
immediately and silently defeated the cooldown.

Therefore:

- The ledger is **ADDITIVE ONLY**. Nothing in the cooldown decision path may
  read it.
- `repo.request(email, app)` stays the single arbiter of "is this email in
  cooldown?" — it is a `SETNX` on a TTL'd Redis key, and that is the correct
  mechanism. **Do not** "improve" it by consulting MongoDB, and **do not** add
  a Mongo-side cooldown check as a fallback for a missing Redis key: that
  re-opens exactly the 031 defect in a new place, and a permanent ledger entry
  would make the cooldown *unbounded* rather than 14 days.
- `clear(..., preserve_request=True)` / `clear_email(..., preserve_request=True)`
  in `core/temp_access.py` stay the mechanism that protects the marker. The
  ledger must not become a second thing to remember to preserve.
- If a ledger write fails, it must **never** change the cooldown outcome. A
  best-effort ledger with a logged failure is correct; a ledger that gates the
  request path is a regression.

## Repository
pole-ai-ml

## What to Do (Implementation Steps)
- [ ] **New collection + repository.** Add a small repository for the
  `temp_access_audit` collection, following the conventions of
  `core/repositories/video_repository.py` (thin class over
  `core.mongo.get_database`, constructor-injectable `Database` for tests).
  Do **not** put a new raw `MongoClient`/database lookup in a controller —
  `core/mongo.py` owns that.
  - Index what the read paths need: `(email, app)` at minimum. Think about
    whether an upsert key on `(email, app)` or on `(email, app, token)` best
    matches the semantics you implement and pin it in a test — the re-entry
    behaviour depends on it.
  - The collection name should be explicit and greppable (`temp_access_audit`,
    as titled) and must not collide with any owned-data collection the purge
    sweeps.
- [ ] **Write at link-issue.** In the request path
  (`auth/controllers/temporary_access.py::request_temporary_access`, after the
  `repo.request(...)` gate is **won** — i.e. only for an accepted request, never
  for a 409), record/refresh the ledger entry with `email`, `app` and
  `link_issued_at`. A rejected (cooldown) request must not create a second
  entry that looks like a new issuance.
- [ ] **Write at window-start.** In
  `TempAccessRepository.start_window` (or its single caller, `verify-code` —
  **choose the one place** that both entry paths share; `start_window` is
  documented as exactly that, and putting the hook there is what stops the
  never-extend rule and the audit from drifting apart), set
  `window_started_at` **only when the call actually created the window** — the
  method already returns `(window, started)` and `started is True` for the
  single winner. A confirmation of an existing window must **not** rewrite
  `window_started_at`; that would corrupt the audit with the *last* re-entry
  time instead of the real start.
  - Mirror the ledger write's failure posture: best-effort + logged, never
    fatal, never on the response path. Do not let a Mongo hiccup turn a
    successful `verify-code` into a 500.
- [ ] **Idempotency on re-entry — explicitly required.** Re-entry is normal,
  not exceptional: a page refresh, a second `send-code`, a re-used link inside
  the live 2h window, a `verify-code` retried after a transient failure. All of
  these must leave **one** coherent ledger row per user+app:
  - `use_count` **increments**; it does not reset, and repeated identical calls
    do not double-count beyond the one flow step they represent;
  - `link_issued_at` and `window_started_at` are **first-write-wins** and are
    never overwritten by a later event (use `$setOnInsert` / `$min`-style
    semantics deliberately, and say which you chose in a comment);
  - re-running the same step twice with the same inputs must not create a
    duplicate document.
- [ ] **`consumed_tokens`.** Record the **identifier** of a token when it is
  spent or expires, so it is recognisable and never honoured again.
  - Store the **identifier**, not a credential: if the identifier is itself the
    `secrets.token_urlsafe(24)` value that travels in the emailed link, then
    storing it durably turns a purge-safe design into a permanent credential
    store. **Decide and document** whether you store the raw identifier or a
    one-way digest (the codebase already has the pattern: the OTP code is
    stored as a **peppered SHA-256 digest**, never the plaintext, in
    `core/otp.py`). A digest is the safer default and preserves the property
    that matters — "recognise this token, never honour it" — without keeping a
    replayable secret. **State the choice and its rationale in the module
    docstring;** a reviewer must not have to guess.
  - Whatever is stored must **never** be usable to start or extend a window.
    The ledger is an observation, not a grant. The `ts_end = ts_start + 2h`
    never-extend rule (ADR-007 Decision 1) and the `SET … nx=True` arbiter in
    `start_window` remain the only things that can open a window.
  - Bound the growth of the array per user so a long-lived entry cannot grow
    without limit inside a single document (the *collection* growing forever is
    a deferred decision; an unbounded array inside one document is just a bug).
    Pin the cap and the eviction order in a test, and say in a comment what
    evicting the oldest identifier means for the guarantee.
- [ ] **The purge must not touch it — prove it.** In
  `core/temp_access_purge.py`, verify by reading the purge path that nothing
  deletes the ledger: the sweep is Mongo-owner-keyed for *owned* collections,
  Redis-keyed for `temp:*`, plus the Keycloak disable. Add an explicit
  regression test that runs a full purge for a user and asserts the ledger row
  **still exists** with its `consumed_tokens` intact. That test is the point of
  the ticket — a future "let's tidy up the database" change must go red here.
  - Add a short comment at the purge site naming the ledger and pointing at
    this ticket, so a reader does not "helpfully" extend the purge to it.
- [ ] **Cooldown regression guard.** Add a test that after a full purge, a
  re-request for the same email+app is still refused (the `temp:req` marker
  survived — 031), and that this refusal **does not** involve the ledger. This
  is the guard against the failure mode described above.
- [ ] **Tests** in `app/pole_api/tests/`, extending the **existing** temp-access
  modules (`test_temp_access.py`, `test_temp_access_endpoints.py`,
  `test_temp_access_purge.py`) — do **not** start a new parallel test module.
  Cover: link-issue writes the row; a cooldown 409 writes nothing; window-start
  sets `window_started_at` **once**; a second `start_window` inside the live
  window does **not** move it; `use_count` increments across re-entries
  without duplication; a spent token lands in `consumed_tokens` exactly once;
  the purge leaves the row intact; a ledger write failure does not fail the
  request or the verification.
- [ ] Keep `pixi run test` green with ≥80% coverage on the modified files.

## Explicitly OUT of scope

- **Retention / pruning / TTL for the ledger — deferred by decision.** ADR-007
  records *retain forever, for now*: the app is a low-traffic demo, and
  unbounded growth is **accepted**. Do **not** add a TTL index, a scheduled
  prune job, an archive tier or a cleanup task in this ticket. A production
  release must add a retention job before real users are onboarded — that is a
  documented follow-up, not a hidden requirement here. The only bound this
  ticket adds is the **per-document** `consumed_tokens` cap described above.
- **No soft-delete / tombstone / anonymisation of owned data.** Owned data
  stays physically deleted. Revisiting that is a new ADR.
- **No change to the cooldown mechanism.** The `temp:req` `SETNX` stays the
  arbiter; the ledger is never consulted for it.
- **No new endpoint and no API surface.** This ticket adds a collection and its
  writes. Reading the ledger back out (an admin/report view) is not in scope.
- **No change to the 2h window semantics** — ADR-007 Decision 1 stays: re-use
  inside a live window is fine, a lapsed window is never re-armed from a stored
  link, and the ledger must not become a way to do so.
- **No index/collection changes to the owned-data collections.**

## Acceptance Criteria (Definition of Done for this Ticket)

- [ ] A `temp_access_audit` record is written at **link-issue** and updated at
  **window-start**, carrying `email`, `app`, `link_issued_at`,
  `window_started_at`, `use_count` and `consumed_tokens`.
- [ ] A cooldown `409` writes **no** new issuance record.
- [ ] Re-entry is idempotent: one document per user+app, `use_count`
  increments, and `link_issued_at` / `window_started_at` are first-write-wins
  (a second `start_window` does **not** move `window_started_at`).
- [ ] A spent or expired token's identifier is recorded exactly once, in a
  form that is **not** a usable credential, and is never honoured again.
- [ ] The purge deletes the user's owned data and leaves the ledger row —
  including `consumed_tokens` — **intact** (proved by a test, not a comment).
- [ ] After a purge, a re-request for the same email+app is **still refused**
  by the `temp:req` cooldown, and no code path consults the ledger to decide
  that (the PAIML-KEYCLOAK-031 invariant holds).
- [ ] A ledger write failure is best-effort and logged; it never changes a
  request's or a verification's outcome.
- [ ] No TTL, prune job or retention policy was added (ADR-007 defers it).
- [ ] The new tests **fail against the pre-change code**; `pixi run test` green
  with ≥80% coverage.

## Integration Tests to Run (Local Verification)

- [ ] Request a link for a fresh email: assert the ledger row exists with
  `link_issued_at` set and `window_started_at` null.
- [ ] Request again immediately: assert `409`, and assert **no second row /
  no changed `link_issued_at`**.
- [ ] Complete `verify-code`: assert `window_started_at` is set and
  `use_count` incremented.
- [ ] Re-open the same link and complete again inside the live window: assert
  one row, `window_started_at` **unchanged**, `use_count` incremented, and the
  2h `ts_end` **not** moved (ADR-007 Decision 1).
- [ ] Burn the code, then try the same token again: assert it is refused
  **and** that its identifier appears in `consumed_tokens`.
- [ ] Let the window lapse and let the sweeper purge the user: assert the
  owned data is gone, the ledger row is **still there**, and an immediate
  re-request is refused by the cooldown.
- [ ] `mongosh` the collection and confirm the stored token identifier is not
  the raw `temp_token` (if the digest choice was taken).
- [ ] Full `pixi run test` green with ≥80% coverage.

## Dependencies
- **Blocks:** None
- **Blocked By:** PAIML-KEYCLOAK-032 (the `send-code` idempotency +
  `already_sent` path is part of the link/code flow whose usage the ledger
  counts; this ticket writes into the same request/verify surface and must not
  race 032's branch changes)

## Estimated Effort
- [M] (Medium 3–5h)

> **Cross-reference:** [ADR-007](../../decisions/ADR-007-temp-access-link-reuse-and-audit-retention.md)
> (Decision 3 — owned data physically deleted, audit ledger retained forever
> with pruning **deferred**; Decision 1 — the never-extend 2h rule this ledger
> must not undermine), PAIML-KEYCLOAK-031 (the `temp:req` cooldown-survives-
> purge invariant that must not be reintroduced as a bug), PAIML-KEYCLOAK-022
> (`start_window`'s `SET … nx=True` arbiter and `ts_end = ts_start + 2h`),
> PAIML-KEYCLOAK-020 / -021 (purge + link-issue surface),
> `core/otp.py` (the store-a-digest-never-the-plaintext precedent), and
> [PLAN_PHASE_12.md](../../plan/PLAN_PHASE_12.md).
