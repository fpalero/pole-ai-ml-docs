# Hardened Analysis Tests — Running Guide (PAIML-POLE-AGENT-012)

This document explains how to run the Phase 6 hardened analysis suite and how
to execute **full-fidelity HA-H5** against a real local PostgreSQL seed.

## What is covered

| ID | Scenario | Assertion |
| :--- | :--- | :--- |
| HA-H5 | Reference threshold discovery | Stored JSON in the DB validates `0 < entrance < execution < 100` and is retrievable via the thresholds endpoint |
| HA-S4 | LLM (`opencode serve`) timeout/down | Retry once, then fallback advice (no crash, error logged); 503 contract when every attempt fails |
| HA-S5 | Missing reference data | 422 `"Reference thresholds not trained"` instead of fabricated feedback |
| Perf | Phase detection | `< 100 ms` on a synthetic 150-frame signal (§9.1) |
| Perf | Coaching feedback | `< 8 s` round-trip with mocked LLM latency (§9.1) |
| Rate | Detection fallback | PD-05 fallback triggers in `≤ 5%` of a representative corpus (§9.2) |

All LLM calls are **mocked** — the suite adds no network dependencies and is
safe to run offline or in CI.

## Quick run (in-memory, no infrastructure)

The default suite replaces the DB with the in-memory repositories
(`InMemoryReferenceRepository` / `InMemoryAttemptRepository`) and the LLM with
stubs. No Postgres, Mongo, Redis or `opencode serve` is required.

```bash
# Dedicated hardening runner (pole-tools gates + API integration tests)
pixi run test-hardening

# Standard runners (the API tests are part of the API suite)
pixi run test-api                # includes app/pola_api/tests/tools/test_hardening_api.py
cd packages/pole-tools && pytest # includes packages/pole-tools/tests/test_hardening_analysis.py
```

Test files:

- `packages/pole-tools/tests/test_hardening_analysis.py` — HA-S4 retry/fallback
  unit tests, phase-detection performance gate, feedback performance gate,
  fallback-rate gate.
- `app/pola_api/tests/tools/test_hardening_api.py` — HA-H5 discovery →
  persistence → retrieval integration tests, HA-S4 503 contract, HA-S5 422
  contract (real `ToolsService` path with the skeleton extraction step stubbed).

## Full-fidelity HA-H5 with a real local PostgreSQL

The in-memory run proves the discovery contract against a stand-in repository.
To prove HA-H5 against the real persistence layer (`PostgresReferenceRepository`):

### 1. Start PostgreSQL

```bash
# Local Postgres via docker (or use your system service)
docker run -d --name pole-ai-pg \
  -e POSTGRES_USER=pole -e POSTGRES_PASSWORD=pole \
  -e POSTGRES_DB=pole_ai \
  -p 5432:5432 postgres:16
```

### 2. Apply the schema migration

```bash
psql "postgresql://pole:pole@localhost:5432/pole_ai" \
  -f app/pola_api/migrations/001_tools_postgres.sql
```

This creates `reference_metrics`, `reference_thresholds` and `attempt_logs`
(JSONB-backed; the exact tables the repos read/write).

### 3. Seed reference_metrics (PAIML-POLE-AGENT-009)

The seeder writes through the tools REST API
(`POST /api/tools/reference/metrics`), so start the API with `DATABASE_URL`
set first, then run the seeder over a labeled-attempts manifest:

```bash
export DATABASE_URL="postgresql://pole:pole@localhost:5432/pole_ai"
pixi run api &                    # tools API persists into PostgreSQL

pixi run seed-reference --manifest attempts.json \
  --data-dir packages/pole-train-model/sources/videos
```

The seeder writes the 24 rows per trick type (3 phases × 8 metrics) via
`save_metrics` into the `reference_metrics` table (idempotent upsert). Verify:

```bash
psql "$DATABASE_URL" -c \
  "SELECT trick_type, phase, metric_name, jsonb_array_length(mean_array)
   FROM reference_metrics WHERE trick_type='STATIC' LIMIT 5;"
```

### 4. Run the API with Postgres and drive HA-H5 manually

```bash
export DATABASE_URL="postgresql://pole:pole@localhost:5432/pole_ai"
pixi run api &
```

Then discover thresholds for a trick type (LLM call — this is the only step
that needs `opencode serve`; for a fully offline full-fidelity check you can
insert a validated config directly, see step 5):

```bash
# 1) Discover -> persisted + returned with 0 < entrance < execution < 100
curl -s -X POST "http://localhost:8000/api/tools/reference/thresholds/discover?trick_type=STATIC" | python3 -m json.tool

# 2) Retrievable via the thresholds endpoint
curl -s "http://localhost:8000/api/tools/reference/thresholds?trick_type=STATIC" | python3 -m json.tool

# 3) Inspect the JSON actually stored in PostgreSQL
psql "$DATABASE_URL" -c \
  "SELECT trick_type, config FROM reference_thresholds WHERE trick_type='STATIC';"
```

The stored `config` must satisfy `0 < end_of_entrance_frame <
end_of_execution_frame < 100` and contain all four
`suggested_numeric_thresholds` keys — the same invariants the automated HA-H5
tests assert (the API test file asserts them against the in-memory repository
that implements the identical `ReferenceRepository` interface).

### 5. Offline full-fidelity alternative (no opencode serve)

If you want the full Postgres persistence path without an LLM call, insert a
validated config directly and confirm the endpoint serves it back:

```bash
psql "$DATABASE_URL" -c \
  "INSERT INTO reference_thresholds (trick_type, config)
   VALUES ('STATIC', '{\"end_of_entrance_frame\": 25, \"end_of_execution_frame\": 70,
     \"suggested_numeric_thresholds\": {\"horizontal_speed_brake\": 0.3,
     \"vertical_speed_cross_zero\": 0.0, \"angular_acceleration_spike\": 2.0,
     \"wrist_stability\": 0.5}}')
   ON CONFLICT (trick_type) DO UPDATE SET config=EXCLUDED.config;"

curl -s "http://localhost:8000/api/tools/reference/thresholds?trick_type=STATIC" | python3 -m json.tool
```

### 6. HA-S5 against the unseeded Postgres DB

Use an empty database (or a fresh schema without the seed) and call analyze
without `phase_frames`: the automatic phase detection has no thresholds to
load and the endpoint must answer 422 `"Reference thresholds not trained"`.

```bash
curl -s -X POST "http://localhost:8000/api/tools/analyze" \
  -H 'Content-Type: application/json' \
  -d '{"video_path": "/path/to/video.mp4"}' \
  -w '\nHTTP %{http_code}\n'
# => {"detail":"Reference thresholds not trained for trick type 'STATIC'"}
# => HTTP 422
```

## Notes

- The performance gates use `time.perf_counter` around pure-Python work with
  mocked latency; they are deterministic and CI-safe (measured ~0.15 ms for
  phase detection, far below the 100 ms budget).
- The fallback-rate corpus is 60 synthetic attempts (59 realistic + 1
  pathological) so the 5% ceiling is exercised with margin.
- Nothing in the suite touches `opencode serve`, `MongoDB` or `Redis`; the
  API tests stub `SkeletonExtractor` so no MediaPipe model asset is needed.
