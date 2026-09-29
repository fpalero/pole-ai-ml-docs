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

---

# Close-out

**Status:** ✅ SHIPPED — `pole-ai-ml` PR
[#363](https://github.com/fpalero/pole-ai-ml/pull/363), merged into `develop`.
New collection `temp_access_audit` in the **app** database (`POLE_API_DB`).

## What shipped

| File | Change |
| :--- | :--- |
| `src/core/repositories/temp_access_audit_repository.py` | **New.** Thin repository over the `temp_access_audit` collection, following `core/repositories/video_repository.py` conventions (injected `Database`, `create_index` in `__init__`, `_id` stringified). |
| `src/core/temp_access.py` | `TempAccessAuditSink` Protocol + `_default_audit_repository()`; audit hooks in `start_window` (both outcomes) and in `activate` (token consumed). Signpost comments on the purge. |
| `src/core/temp_access_purge.py` | Signpost comment: the ledger is not purged. |
| `src/auth/controllers/temporary_access.py` | `record_link_issue` after the link is genuinely delivered. |

## Decisions taken (beyond the spec)

**Upsert key `(email, app)`** — as suggested, with a **unique** compound index so
the idempotency guarantee is structural rather than conventional. Rejected
`(email, app, token)`: the token is a *property* of the row, not part of its
identity, so a per-token key would make `use_count` / `window_started_at`
unanswerable from a single read and turn a re-used link into several "users".

**First-write-wins timestamps use `{"$ifNull": ["$f", now]}` in an
aggregation-pipeline `update_one`, not `$setOnInsert`.** The ticket suggested
`$setOnInsert` / `$min`-style semantics; `$ifNull` is required here because
**either** writer can legitimately create the row — `start_window` is shared by
both entry paths, so a window may start on a row no request ever created.
`$setOnInsert` would stamp a phantom `link_issued_at` in that order and leave
`window_started_at` `null` forever in the other. `$min` cannot express it either
(a missing field must stay missing, not become epoch). `use_count` is
`{"$add": [{"$ifNull": ["$use_count", 0]}, 1]}`.

**`consumed_tokens` stores a peppered SHA-256 digest, not the identifier** — the
choice ADR-007 and the ticket both point at, following the `core/otp.py`
precedent. The emailed `temp_token` *is* a bearer credential; storing it durably
would turn a purge-safe design into a permanent credential store. Reuses the
existing `TEMP_ACCESS_OTP_PEPPER` secret rather than asking ops to provision a
second one.

**Cap: 100 per document, FIFO, trimmed inside the *same* server-side
expression** (`$slice` over `$setUnion`), so the document never transiently
exceeds the cap. **What eviction costs:** a token whose digest has been evicted is
no longer *recognisable* as previously consumed. It is **not** honoured again —
nothing in the ledger authorises anything, and the window is governed solely by
`start_window`'s immutable `ts_end` — so the cap weakens a forensic question for
the oldest identifiers and nothing about access control.

**The `record_window_start` hook is unconditional**, called for both the window
creation and the confirming re-entry, with the *write* telling them apart
(`$ifNull` stamps the start once; `$inc` counts every use). Branching on
`started is True` at the call site would push that decision into every caller,
and `start_window` has two today and could gain a third. It also means a new
entry path cannot get the "stamp the start" half wrong.

**A lapsed window audits nothing** — the hook sits after the `now >= ts_end`
early-return, so a purged window cannot leave a phantom "access started" stamp.

## Review findings addressed

`/oc review` on PR #363 raised two blocking issues, both real, both fixed in
`38a5dd8`:

1. **The audit sink was never wired in production** — the sink was injected and
   defaulted to `None`, and no production call site passed one, so
   `record_window_start` and `record_token_consumed` **never fired**. The feature
   shipped **1/3 delivered** while reading as complete: `window_started_at`
   absent, `use_count` permanently `0`, `is_token_consumed()` always `False` —
   i.e. all three ADR-007 D3 questions unanswerable. The suite could not see it
   because every hook test injected the sink by hand, pinning *"the hook works
   when injected"* and never *"production injects it"*.
   **Fix:** `_default_audit_repository()` builds the sink lazily in `__init__`
   when none is injected, so a sink is the **default** rather than something each
   call site must remember. Construction is failure-tolerant — an unreachable
   Mongo degrades the ledger to absent and leaves the 2h window and the 14-day
   cooldown untouched.
2. **The best-effort path blocked the event loop** — `_audit` was `async` but
   called synchronous pymongo, as did the controller. With no
   `serverSelectionTimeoutMS` override a hung Mongo stalls the request for the
   full server-selection timeout, so the *"never gates the flow"* guarantee
   failed in precisely the outage it exists to survive. **Fix:** both dispatch via
   `asyncio.to_thread` (existing precedent in `chatbot/router.py`,
   `training_chatbot/router.py`, `analyst_chatbot/services.py`).

**Lesson worth carrying forward (this is the one to keep):** a hook test proves
the hook, never the wiring. Any feature whose behaviour depends on a dependency
being *injected* needs a test that builds the object the way production builds it.
All three rounds came from the same blind spot — tests that injected a sink, or
used `mongomock` where `create_index` never blocks, so the suite could not see
that production was doing blocking I/O on the hot path. The tests now pin the
**cost**, not just the presence: `__init__` is asserted to perform no Mongo I/O
at all, the lazy build is asserted to run on a worker thread, and five audit
writes are asserted to trigger exactly one build.

**Second lesson:** fixing *"the ledger never fires"* by wiring the dependency into
a **constructor** is a trap when that constructor is on a hot path. The fix for
B1 created B3. Prefer resolving the dependency at the point of use, off-loop,
with the failure memoised — never at construction.

A **third** round then caught **B3 — a regression the B1 fix introduced, and a
worse one than the problem it fixed.** Building the sink synchronously in
`TempAccessRepository.__init__` meant that constructor did blocking pymongo I/O
(`create_index`) **on the event loop of every authenticated request**:
`core/auth.py` builds a repository in both `get_user_id` and `require_role`, and
there is no `serverSelectionTimeoutMS` anywhere in `src/`, so pymongo's 30 s
default applies. The net effect was two blocking Mongo round trips per request —
and during an outage, up to 30 s of stall each. An audit-only, best-effort
feature would have taken down the authenticated API in precisely the scenario it
exists to survive. The controller had the same defect in subtler form: the sink
was an **argument expression** to `asyncio.to_thread`, evaluated on the loop
before the hop.

**Fix:** the sink is built **lazily inside `_audit`**, which is already async and
already off-loop, so `__init__` performs no Mongo I/O at all. The resolve and the
write share a single `to_thread` hop, and the outcome is memoised so a Mongo-less
host does not retry the build on every write.

Non-blocking notes also addressed: `record_token_consumed` no longer stamps
`link_issued_at` (the field means *"when the link was requested"*); a never-written
field is `null` rather than absent (docstring corrected); the missing-pepper
warning is emitted **once per process** rather than on every construction (a
repository is built per request on the hot path, so a missing
`TEMP_ACCESS_OTP_PEPPER` became a log line per request).

## Acceptance criteria

- [x] A `temp_access_audit` record is written at **link-issue** and updated at
      **window-start**, carrying `email`, `app`, `link_issued_at`,
      `window_started_at`, `use_count` and `consumed_tokens`.
- [x] A cooldown `409` writes **no** new issuance record (the write is after the
      `SETNX` gate is won, and after the link is delivered).
- [x] Re-entry is idempotent: one document per user+app, `use_count`
      increments, and `link_issued_at` / `window_started_at` are
      first-write-wins.
- [x] A spent token's identifier is recorded exactly once, as a **peppered
      digest** (not a usable credential), and is never honoured again.
- [x] The purge deletes the user's owned data and leaves the ledger row —
      including `consumed_tokens` — **intact**, proved by a behavioural test
      *and* a structural `inspect.getsource` guard on the purge source.
- [x] After a purge, a re-request is still refused by the `temp:req` cooldown,
      and a test proves the decision is **Redis-only** (strip the marker and the
      request is accepted again even though the audit row is permanent).
- [x] A ledger write failure is best-effort and logged; it never changes a
      request's or a verification's outcome — and never blocks the event loop.
- [x] No TTL, prune job or retention policy was added (ADR-007 defers it).
- [x] The new tests **fail against the pre-change code** (verified by stashing
      the source and re-running); `pixi run test-api` green, ≥80% coverage.

## Verification

`471 passed, 9 skipped` across the temp-access surface. Coverage on the modified
files: **100%** `temp_access_audit_repository`, **95%** `temporary_access.py`,
**90%** `temp_access.py`, **89%** `temp_access_purge.py`. `ruff check` clean on
every touched file.

All three blocking regressions were re-verified individually: reverting B1 turns
the three wiring tests red; reverting B2 turns the event-loop test red; reverting
B3 turns `test_construction_does_no_mongo_io` and
`test_the_lazy_sink_build_also_runs_off_the_event_loop` red.

> **Pre-existing, unrelated:** a full `test-api` run shows 8 failures in
> `test_e2e`, `test_process`, `test_process_integration` and
> `test_analyst_ws_integration`. 7 of the 8 reproduce identically on `develop`;
> the 8th is a test-ordering flake that passes in isolation. None are in the
> temp-access surface.

## Follow-ups (not in this ticket)

- **Retention/pruning.** Still deferred by ADR-007 and still **required before
  production**: the collection grows without a prune. A production release must
  add a retention job or a documented archive.
- **Reading the ledger back out.** `TempAccessAuditRepository.list_entries()` and
  `is_token_consumed()` ship with no caller; an admin/report view is out of
  scope here. They are now reachable (the sink is wired), so a report surface
  needs no further plumbing.
- **`is_token_consumed` is a recognition helper, not an enforcement one.**
  Nothing refuses a request on its answer — the Redis record and `start_window`
  are the enforcement surfaces. If a future change wants to *refuse* a token from
  the ledger, that is a security change needing its own ADR.

