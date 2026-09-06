# 05 — Real-Time Systems & Full-Stack ML

> Real-time recognition over WebSockets, an LLM agent wrapping ML tools, and
> coaching feedback computed from metrics. The "product spine" of pole-ai.
> Grounded in `app/pole_api`, `app/pola_agent`, and `docs/diagrams/pola_agent/`.

## Core articles in this theme

| ID | Title | Difficulty | Primary audience |
| :--- | :--- | :--- | :--- |
| E1 | Real-Time Recognition: WebSockets, Circular Buffers & Vote Consensus | Advanced | ML/CV + backend |
| E2 | Wrapping ML in an Agent: ReAct Loop + Tool Registry | Advanced | Backend |
| E3 | Coaching Feedback from Metrics: Z-Score Outliers + LLM | Intermediate | All |
| E4 | Taking an Agent to Production: Sessions, Rate Limits & Metrics | Advanced | Backend |
| E5 | Custom ReAct vs LangGraph: Two Ways to Build the Same Agent | Advanced | Backend + ML/CV |
| E6 | Design Tokens → Real UI: An AI-Generated Angular Frontend | Intermediate | Frontend + PM |
| E7 | Feature-Sliced FastAPI: Structure That Never Outgrows You | Intermediate | Backend |
| E8 | The 'No Class States' Refactor: Deriving State from Data | Intermediate | Backend |
| E9 | Deterministic Guardrails for LLM Agents | Intermediate | Backend + ML/CV |
| E10 | Model Registry UI: The Human Gate for ML Deploys | Intermediate | Frontend |
| E11 | Training Studio: Launching Long ML Jobs From a Browser | Intermediate | Frontend |

## What makes this theme sellable

- **E1** hits the <100 ms round-trip goal with a circular 30-frame buffer and
  3/5 vote consensus — a concrete recipe for "ML in real time", a topic full
  of vague posts and short on implementations.
- **E2** shows how to expose heavy, long-running ML operations (crop, shift) as
  job-mode tools inside a bounded ReAct agent — very differentiated.
- **E3** is a compelling "AI sports coach" case study (Dartfish/Hudl comparison)
  with real logic: z-score outlier detection against a cohort, laundry-list
  improvement plans, and layered pose correction.

## Source docs

- `docs/diagrams/pola_agent/FLOW.md`, `docs/diagrams/chatbot/CLASSES.md`
- `docs/app/pola_agent/implementation_plan.md`, `docs/app/pola_agent/pose_correction.md`
- `docs/app/pola_agent/agent_requirements.md` (coaching prompt LLM-CF-03)
- `docs/app/pole_api/plan/PLAN_PHASE_18.md`, `PLAN_PHASE_16.md`

---

## Docs per audience

- [`ml-cv.md`](ml-cv.md) — ML / computer vision engineers
- [`fullstack-backend.md`](fullstack-backend.md) — full-stack / backend engineers
- [`junior-mixed.md`](junior-mixed.md) — mixed beginner → intermediate
- [`tech-entrepreneur.md`](tech-entrepreneur.md) — entrepreneur / technical PM