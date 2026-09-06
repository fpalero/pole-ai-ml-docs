# Theme 05 — Real-Time & Full-Stack · Audience: Full-Stack / Backend Engineers

> The backend engineer's playground: WebSocket chat over ML, agent tool
> registries, job-mode handlers, and rate limiting for LLM traffic.

## Catalog

### E1 (adapted) — WebSocket Streaming of ML Results, Done Reliably
- **Difficulty:** Intermediate/Advanced
- **Type:** Backend guide
- **Hook:** "Sockets + long inference = sadness, unless you design the wire protocol first."
- **Description:** Chatbot/analyst WebSockets (`/ws/chat`, `/ws/analyst-chat`):
  session handshake, `agent_reply` + job-event streaming frames, rate limiting
  (429-equivalent WS frame), and resilience (auto-reconnect, session resume).
- **Grounding:** `docs/diagrams/pola_agent/FLOW.md`, `docs/app/pola_agent/implementation_plan.md` (Phase 3), `docs/app/pole_api/plan/PLAN_PHASE_18.md`.
- **Sellable angle:** Concrete websocket-over-ML protocol design — scarce content.

### E2 — Wrapping ML in an Agent: ReAct Loop + Tool Registry
- **Difficulty:** Advanced
- **Type:** Architecture guide
- **Hook:** "Let the LLM call your ML — but bound its loops and make the heavy work a job."
- **Description:** `ReActAgent` (bounded tool-call loop, max_iterations, error
  capture, off-script rephrase) + `ToolRegistry` (sync tools like
  `histogram`/`similarity`; job-mode tools like `crop`/`shift`). Shows how to
  marshal long-running ML ops through an LLM agent safely.
- **Grounding:** `docs/diagrams/chatbot/CLASSES.md`, `docs/diagrams/pola_agent/FLOW.md`.
- **Sellable angle:** Cutting-edge agent engineering, production-grounded.

### E3 (adapted) — Building an AI Coach Service: Caching, Retries, Schemas
- **Difficulty:** Intermediate
- **Type:** Backend guide
- **Hook:** "LLM output is a cacheable, retryable, schema-validated resource — run it like one."
- **Description:** The `CoachService` mechanics: schema-validated LLM generation
  with retry, caching summaries/plans on the video doc, deterministic fallback
  (backfill) when the LLM fails, and exposing plans as chatbot tools.
- **Grounding:** `docs/app/pole_api/phase-26-analyst-coach-tools/PAIML-POLE-API-076/077.md`.
- **Sellable angle:** "LLM reliability patterns" every backend team needs.

### E4 — Taking an Agent to Production: Sessions, Rate Limits & Metrics
- **Difficulty:** Advanced
- **Type:** Backend guide
- **Hook:** "Your agent answers well. Does it handle 200 concurrent chatters?"
- **Description:** The session/observability layer used by `pole-chatbot`:
  `ChatbotSession` schema with Redis + Postgres repositories
  (read-through/write-through caching), a Redis sliding-window `RateLimiter`
  (429 + WS equivalent), and a `MetricsCollector` for tool latency + LLM tokens.
- **Grounding:** `docs/packages/chatbot/PLAN.md` (Phase 4), `docs/diagrams/chatbot/CLASSES.md`.
- **Sellable angle:** Production-readiness of agents is the #1 gap in agent
  tutorials today.

### E5 — Custom ReAct vs LangGraph: Two Ways to Build the Same Agent
- **Difficulty:** Advanced
- **Type:** Comparative deep-dive
- **Hook:** "Same agent, two architectures: how much does a framework actually buy you?"
- **Description:** `ReActAgent` (hand-rolled loop) vs `PoleLangGraphAgent`
  (`StateGraph` with agent/tool nodes + conditional routing). Compares token
  accounting, control flow, testability, and where LangGraph earns its keep —
  plus the `OllamaLLM` adapter behind an OpenAI-compatible client.
- **Grounding:** `docs/packages/chatbot/PLAN.md` (agent.py, agent_langgraph.py, llm.py),
  `docs/diagrams/chatbot/CLASSES.md`.
- **Sellable angle:** Honest framework comparison is rare; debates are high-traffic.

### E7 — Feature-Sliced FastAPI: Structure That Never Outgrows You
- **Difficulty:** Intermediate
- **Type:** Backend architecture guide
- **Hook:** "Routers sprawl; slices scale. Here's a FastAPI layout organized by feature."
- **Description:** Organize a FastAPI app by slices (crawler, training, video,
  tools) over a shared `core`, with an async job pattern where every long op
  returns `202 {job_id}` and the client polls. Cross-slice touchpoints (shared
  video collection, shared embed function) documented up front. The same
  package is mountable as an app or a slice.
- **Grounding:** `docs/app/pole_api/slices.md`, `docs/diagrams/pole_api/CLASSES.md`, `FLOW.md`, `docs/app/pole_api/implementation-plan.md`.
- **Sellable angle:** Concrete FastAPI scaling pattern; most tutorials stop at
  one router + one model.

### E8 — The 'No Class States' Refactor: Deriving State from Data
- **Difficulty:** Intermediate
- **Type:** Refactoring/domain-design case study
- **Hook:** "We deleted the status machine — and the app got simpler."
- **Description:** Removing class-level states (`core/status.py` gone): each
  endpoint validates by related entities instead. A video is 'train-ready'
  when its windows exist and are flagged, not because a status bit says so.
  Covers propagation (video flag → windows) and the danger this removes.
- **Grounding:** `docs/app/pole_api/slices.md` (§Modelo de estados),
  `docs/app/pole_api/phase-18-analyst-chatbot/PAIML-POLE-API-050.md`.
- **Sellable angle:** Real refactor-with-conviction story that backend teams
  relate to; ties into domain-driven design.

### E9 — Deterministic Guardrails for LLM Agents
- **Difficulty:** Intermediate
- **Type:** Agent-safety implementation guide
- **Hook:** "Your ReAct loop shouldn't trust the LLM to say 'yes' — it should match words."
- **Description:** A diff-driven pattern for LLM-agent safety that survives
  prompt drift: confirmation detected by word-matching (never an LLM judgment),
  tool calls gated on session state (crop present? confirmed?), off-script
  recovery with a rephrase budget that yields to a fallback, and a synthetic
  `[SESSION STATE]` block injected each turn. One engine shared by a hand-rolled
  ReAct loop and a LangGraph agent.
- **Grounding:** `packages/chatbot/src/pole_chatbot/guardrails.py` (GuardrailEngine,
  `is_confirmation_message`, `recover_offscript`).
- **Sellable angle:** Deterministic guardrails are SEO-rich, hot, and almost
  never shown as real code; every agent builder needs this.