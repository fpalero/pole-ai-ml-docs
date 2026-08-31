# Fase 21 — Coach Prompts (LLM coaching layer sobre el análisis) — 📋 PLANNED

> Plan maestro: [PLAN.md](../PLAN.md) · Decisiones previas: análisis de integración 2026-08-23 (Opción A elegida por el PO)

## Contexto

The athlete-facing tabs (Summary / Plan / Pose) need LLM-generated coaching content. Today only the
Plan tab has agent content (free-text `agent_reply` parsed by the FE); Summary and Pose are purely
rule-based (z-score cards / detection callouts).

The PO selected **Option A**: deterministic, cacheable one-shot coach endpoints backed by a
**prompt registry** — three task-specific prompts, each with a strict JSON output contract:

1. **Performance Summary** — "State of the Union" coaching summary from training statistics.
2. **Improvement Plan** — time-bound progression roadmap toward a target trick.
3. **Static Pose Analysis** — biomechanical breakdown of the pose at the annotated frame.

**PO decisions locked:**

- The LLM **does NOT see images** (text-only `OllamaLLM`). The pose-analysis input is the
  **landmarks + biometric data + signals data** (per-phase metric deviations, z-scores,
  detection issues) — never the JPEG.
- Inputs are gathered **deterministically** from existing repos/facades (no ReAct loop, no tool
  calls inside the coach flow). The chat agent remains separate.
- Outputs are **persisted** on the video doc so tabs render without a live chat session.

## Alcance

### 1. Prompt registry (`analysis/services/coach_prompts.py`)

Three template constants + builder functions that fill an input contract and declare the expected
JSON schema. Each prompt keeps the coaching persona (elite pole coach, biomechanics background),
grounds every claim in the supplied numbers ("never invent metrics"), mirrors the user language
(ES/EN), and demands **strict JSON** matching the schema.

| Constante | Entrada (datos reales disponibles) | Salida JSON |
| :--- | :--- | :--- |
| `SUMMARY_COACH_PROMPT` | `z_mean`, `scores` per phase, `detections[]`, `critical_frame/phase/metric`, `trick_label`, `total_frames`, classification outcome | `{summary, critical_insight, focus_next_session}` |
| `PLAN_COACH_PROMPT` | summary fields + detected errors + `target_trick` (request body) + optional `athlete_notes` | `{issue, weeks[4]: {week, focus, drills[]}, bail_strategy}` |
| `POSE_COACH_PROMPT` | `build_pose_issues()` hints, per-phase metric deviations (landmark-derived M-01..M-08 z-scores), signal curve stats (`resampled` aggregates) — **no image** | `{biomechanical_flaw, correction, aesthetic_feedback, action_step}` |

> Note: the original example prompts referenced stats the system does not track (training
> frequency, grip endurance, flexibility). The templates are rewritten around the actual summary
> contract; athlete-profile stats are out of scope for v1.

### 2. Coach services + persistence

New `analysis/services/coach_service.py`: one service class per action (or one class, three
methods) that gathers data via the existing repositories (`AnalysisHistogramRepository`,
`AnalysisVideoRepository`, `AnalysisLandmarkRepository`), fills the template, makes **one**
`OllamaLLM` call (reuse the `settings.ollama_model`/`ollama_host` config; the client instance is
already exposed as `app.state._analyst_chatbot_llm`), validates/parses the JSON reply (one retry on
parse failure), and persists the result on the video doc:

- `videos.coach_summary` — `{content, model, generated_at}`
- `videos.coach_plan` — `{target_trick, content, model, generated_at}`
- `videos.coach_pose` — `{frame, content, model, generated_at}`

Regeneration overwrites (idempotent last-write-wins). LLM-down / invalid-JSON degrades to a
structured error payload (`503`-shaped detail) — never a crash.

### 3. Endpoints (`analysis/controllers/videos.py`)

| Endpoint | Método | Descripción | Nuevo |
| :--- | :--- | :--- | :--- |
| `/api/analysis/videos/{video_id}/coach-summary` | GET | Generate-or-return cached performance summary | **Nuevo** |
| `/api/analysis/videos/{video_id}/coach-plan` | POST | Generate plan for `target_trick` (body) | **Nuevo** |
| `/api/analysis/videos/{video_id}/pose-analysis` | GET | Generate-or-return cached pose breakdown | **Nuevo** |

Semantics: first call generates + caches (may take seconds — document the latency expectation);
subsequent calls return the cached payload. A `POST .../coach-summary?refresh=true`-style
regeneration flag (or `DELETE` of the cached field) is decided at ticket level.

## Architectural Layering

- **Domain:** coach output DTOs (`CoachSummaryOut`, `ImprovementPlanOut`, `PoseAnalysisOut`) +
  persisted envelope (`{content, model, generated_at}`).
- **Application:** `CoachPromptBuilder` (registry), `CoachService` (gather → prompt → LLM →
  validate → persist).
- **Infrastructure:** `OllamaLLM` (reuse `packages/chatbot`), analysis repositories (read-only
  reuse), `analysis-db.videos` doc extension.
- **Presentation:** 3 routes in `analysis/controllers/videos.py`.

## Implementation Roadmap

### Phase A: Prompt registry (ticket PAIML-POLE-API-062)

- [ ] `analysis/services/coach_prompts.py`: 3 templates + builder functions + JSON schema constants.
- [ ] Unit tests: builders fill every field; templates forbid invented metrics; schemas documented.

### Phase B: Services + persistence (ticket PAIML-POLE-API-063)

- [ ] `CoachService` with injectable repos + LLM client (hermetic tests, no Mongo/Ollama needed).
- [ ] JSON validation with single retry; structured degradation payloads.
- [ ] Persist envelopes on the video doc; regeneration semantics.

### Phase C: Endpoints + integration tests (ticket PAIML-POLE-API-064)

- [ ] Routes + Pydantic response models in `analysis/schemas.py`.
- [ ] Integration tests with mocked LLM (happy path, LLM-down, video-not-analyzed 409/422, regenerate).
- [ ] Update diagrams (`docs/diagrams/pola_api/CLASSES.md` §6) + `POLE-API.md` endpoint list.

## Quality Gates

- **Unit Tests:** `pixi run test-api`.
- **Integration Tests:** guarded `_testing` DBs (`analysis_db_testing`); LLM always mocked in CI.
- **Coverage Requirement:** ≥ 80%.
- **Latency:** one-shot LLM call bounded (< 10 s soft budget); no job infrastructure needed for v1.

## Use Cases

### UC-C1: Coach summary happy path
- **Given** an analyzed video with scored histogram
- **When** `GET .../coach-summary`
- **Then** `200` with `{summary, critical_insight, focus_next_session}` grounded in the stored z-scores
- **And** the envelope is cached on the video doc

### UC-C2: Cached read
- **Given** a video with `coach_summary` already persisted
- **When** `GET .../coach-summary`
- **Then** `200` cached payload, no LLM call (observable via mock call count)

### UC-C3: Improvement plan with target trick
- **Given** analyzed video + body `{"target_trick": "ayesha"}`
- **When** `POST .../coach-plan`
- **Then** `200` with 4-week roadmap JSON incl. `bail_strategy`

### UC-C4: Pose analysis from signals only
- **Given** analyzed video with detections
- **When** `GET .../pose-analysis`
- **Then** `200` with biomechanical breakdown derived ONLY from issues/z-scores/landmark stats
- **And** the request never reads/sends any image bytes

### UC-C5: Video not analyzed
- **Given** a video without scored histogram
- **When** any coach endpoint
- **Then** `409`/`422` structured detail ("run the analysis pipeline first")

### UC-C6: LLM unavailable
- **Given** Ollama down
- **When** any coach generate call
- **Then** structured `503` detail; cached payload still served when present

## Risks and Mitigations

- **Risk:** LLM returns malformed JSON. **Mitigation:** schema-validated parse + 1 retry, then
  structured degradation; raw reply logged for debugging.
- **Risk:** hallucinated metrics. **Mitigation:** prompt hard-rule "never invent values"; post-check
  that numeric tokens appear in the input payload (ticket-level decision if enforced or advisory).
- **Risk:** slow generation blocks the tab. **Mitigation:** cached-read semantics + documented soft
  budget; job-mode deferred to a later phase if needed.
- **Risk:** prompt drift between chat agent and coach endpoints. **Mitigation:** single registry
  module is the only prompt source; chat agent may import the same personas later.

## Open Questions

- Regeneration UX (refresh flag vs explicit button) — decide at ticket 064.
- Enforce numeric-grounding post-check (reject replies citing unknown values)? — decide at ticket 063.
