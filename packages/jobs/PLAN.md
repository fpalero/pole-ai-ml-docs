# Implementation Plan — `jobs` (`pole-jobs` shared job infrastructure)

> **Status:** Complete for v1 — Job model, Mongo `JobRepository`, Redis `JobQueue`, Redis pub/sub
> events, `JobWorker` (retries/backoff/cancel), `JobOrchestrator`, FastAPI `JobRouter` mixin.
> Unit-tested with fakeredis + mongomock; consumed by `packages/chatbot`. Future work: real
> Redis/Mongo CI integration, retry policy per job type, metrics/observability, migration of
> existing `pola_api` thread-runner jobs.
> **Source docs:** `docs/app/pola_agent/implementation_plan.md` §13 (jobs package + chatbot).

---

## 1. Feature Context & Objective

- **Goal:** Shared, durable job infrastructure used by both `app/pola_api` and `packages/chatbot`:
  enqueue long-running work (crop, shift, future heavy tools), persist state in Mongo, signal
  progress via Redis pub/sub, and expose a FastAPI router for submit/poll/cancel plus a
  WebSocket progress stream.
- **Non-Functional Constraints:** Mongo = authoritative job state; Redis = signal/queue only
  (FIFO of job ids); publish failures logged never raised; exponential backoff retries; cancel sets
  `stopped`; injectable clients for tests.
- **Affected Components:**
  - `packages/jobs/src/pole_jobs/` — `models.py`, `repository.py`, `queue.py`, `events.py`,
    `worker.py`, `orchestrator.py`, `router.py`.
  - `packages/jobs/tests/` — unit tests (fakeredis/mongomock) across all modules.
  - `packages/jobs/docker-compose.yml` — dev Redis (`redis:7`).
  - Consumers: `packages/chatbot` (crop/shift jobs), future `pola_api` new job types.
- **Assumptions:** Redis + Mongo reachable (dev via docker-compose); job handlers are
  `Callable[[JobContext, dict], Any]`; WS progress route uses a thread + queue bridge.

---

## 2. Architectural Layering (The "Where")

- **Domain:** `Job` dataclass (`type, payload, id, status, progress, result, error,
  ws_connection_id, queue, attempts, max_retries, cancel_requested, description, timestamps`);
  statuses `pending|running|done|failed|stopped`; event names `job:started|progress|done|error`.
- **Application:** `JobWorker` (dispatch, progress, retry/backoff, cancel), `JobOrchestrator`
  (submit/get/list/cancel/worker/subscriber).
- **Infrastructure:** `JobRepository` (Mongo), `JobQueue` (Redis), `JobEventPublisher`/
  `JobEventSubscriber` (Redis pub/sub).
- **Presentation:** `JobRouter` (FastAPI) — `POST /api/jobs`, `GET /api/jobs/{id}`,
  `GET /api/jobs`, `POST /api/jobs/{id}/cancel`, `WS /api/jobs/{id}/progress`.

---

## 3. Implementation Roadmap (Atomic Steps)

### Phase 1: Core job infrastructure — ✅ DONE
- [x] `Job` model + `utcnow` + JSON-safe `to_dict` (+ bson ObjectId handling).
- [x] `JobRepository` — create/get/update/list/cancel/delete over Mongo `jobs`.
- [x] `JobQueue` — FIFO push/pop (blocking blpop)/pending/clear over Redis.
- [x] `JobEventPublisher` / `JobEventSubscriber` — pub/sub with `ws_connection_id` passthrough;
  subscriber honors stop_event (poll loop).
- [x] `JobWorker` — run_once/run_forever, progress via `JobContext`, `JobCancelled` → `stopped`,
  exponential backoff retries, orphan-id drop, failure formatting.

### Phase 2: Orchestrator + router — ✅ DONE
- [x] `JobOrchestrator` — submit/get/list(by queue)/cancel/worker/subscriber; injectable DB+Redis.
- [x] `JobRouter` (FastAPI mixin) — submit (201), get (404), list (filters), cancel (409/404), WS
  progress relay filtered by `task_id`.
- [x] Unit tests: models, queue, events, worker (incl. retry/cancel), repository, router.

### Phase 3: Future — hardening & adoption
- [ ] Tests live integration suite against real Redis/Mongo in CI (`test-chatbot-live` currently
  exercises real stack; add a dedicated `pixi run test-jobs-live`).
- [ ] Infrastructure per-type retry policy + dead-letter queue.
- [ ] Infrastructure metrics/observability: job duration histograms, queue depth, event counters.
- [ ] Application migrate `pola_api` thread-runner jobs (process, embed, retrain, crawl, cut,
  upload) to `pole-jobs` when the app consolidates with chatbot.
- [ ] Application job descriptions / richer result payloads (`Completed N, Skipped N, Failed N`).

---

## 4. Quality Gates & Testing Commands (DoD)

- **Unit Tests:** `pixi run test-jobs` (pytest in `packages/jobs`, fakeredis + mongomock) — ≥ 80%.
- **Integration Tests:** `pixi run test-chatbot-live` (real Redis/Mongo/ffmpeg E2E through the
  worker); optional `test-jobs-live` (future).
- **Automation:** CI runs `pixi run test-jobs` + `test-chatbot`.
- **Database Target:** Mongo `jobs` collection (chatbot integration uses `pole_chatbot_testing`);
  Redis dev via `pixi run redis-up`.
- **Coverage Requirement:** ≥ 80%.
- **Additional Checks:** `pixi run redis-up` / `redis-down`; publish failures never crash the worker.

---

## 5. Defined Use Cases (Gherkin + Technical Matrix)

### UC-JB-01: Submit and poll a job
- **Given** a running orchestrator with worker + registered handler
- **When** user submits `POST /api/jobs` with `{"type":"crop","payload":{...}}`
- **Then** system returns HTTP `201` with `{id, status:"pending"}`
- **And** `GET /api/jobs/{id}` transitions `pending → running → done` with `result` and `progress=1.0`

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `/api/jobs`, `/api/jobs/{id}` |
| Request Method | POST / GET |
| Required Headers | `Content-Type: application/json` |
| Payload Example | `{"type":"crop","payload":{"src":"x.mp4","start":0,"end":5}}` |
| DB State (Before) | no job doc |
| DB State (After) | `jobs` doc `done`, `finished_at` set; Redis queue drained |

### UC-JB-02: Job failure with retries
- **Given** a handler that fails transiently
- **When** the worker executes it (max_retries=2, backoff)
- **Then** attempts increment; on final failure status = `failed` and `job_error` published
- **And** `error` contains exception type + message

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | worker loop (internal) |
| Request Method | n/a |
| Required Headers | n/a |
| Payload Example | handler raising after N attempts |
| DB State (Before) | job `pending` |
| DB State (After) | job `failed`, attempts == max_retries+1, error set |

### UC-JB-03: Cancel a running job
- **Given** a `running` job
- **When** user submits `POST /api/jobs/{id}/cancel`
- **Then** system returns HTTP `202`
- **And** the handler's `check_cancelled` raises `JobCancelled` → status `stopped`

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `/api/jobs/{id}/cancel` |
| Request Method | POST |
| Required Headers | `Content-Type: application/json` |
| Payload Example | `{}` |
| DB State (Before) | job running |
| DB State (After) | job `stopped`; already done → 409; missing → 404 |

### UC-JB-04: WebSocket progress relay
- **Given** a job event flow with a matching `ws_connection_id`
- **When** the job runs and the WS `/api/jobs/{id}/progress` is open
- **Then** the socket receives `job_started`, `job_progress`, `job_done` (or `job_error`) payloads
- **And** payloads not matching the `task_id` are filtered out

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `WS /api/jobs/{id}/progress` |
| Request Method | WebSocket |
| Required Headers | `Upgrade: websocket` |
| Payload Example | n/a (server push) |
| DB State (Before) | job queued |
| DB State (After) | events relayed in order; mismatch filtered |

### UC-JB-05: Submit a job with WS connection binding
- **Given** a chatbot WS session
- **When** a job-mode tool submits a job with `ws_connection_id`
- **Then** the publisher includes `ws_connection_id` in every event payload
- **And** the chatbot relay forwards only events for that socket

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `POST /api/jobs` (via tool) |
| Request Method | POST |
| Required Headers | `Content-Type: application/json` |
| Payload Example | `{"type":"crop","payload":{...},"ws_connection_id":"<uuid>"}` |
| DB State (Before) | no job |
| DB State (After) | job doc stores `ws_connection_id`; events carry it |

---

## 6. Risks and Mitigations

- **Risk:** Redis as single signal → lost job if worker dies after pop. **Mitigation:** Mongo holds
  authoritative state; worker drops orphan ids; restart re-queues.
- **Risk:** publish failures crash the worker. **Mitigation:** publisher logs, never raises.
- **Risk:** `blpop` blocks stop_event. **Mitigation:** subscriber uses `pubsub.get_message(timeout=0.5)`
  poll loop honoring stop_event.
- **Risk:** two host apps sharing the queue namespace. **Mitigation:** per-queue isolation
  (`queue_name`), orchestrator list filtered by queue.
- **Risk:** existing `pola_api` thread jobs diverge from this contract. **Mitigation:** documented
  migration path (Phase 3); both share the same status vocabulary today.

---

## 7. Open Questions and Decisions

- Decision: Mongo authoritative, Redis signal-only (FIFO of ids).
- Decision: `ws_connection_id` on the Job for chatbot event routing.
- Decision: v1 scope = long tools (crop, shift); existing training jobs stay on the thread runner.
- Open: dead-letter queue + per-type retry policy defaults.
- Open: when to migrate `pola_api` thread jobs to this package.
- Open: whether job `description`/result formatting moves here or stays in `pola_api`.
