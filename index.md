# Documentation Index — `pole-ai`

> Central navigation for the repository's documentation. All diagrams are Mermaid and render on
> GitHub / VS Code.

---

## 📌 Overview

| Doc | Description |
| :--- | :--- |
| [Repository Development Status](DEVELOPEMENT.md) | All projects, phases, phase status, and ticket descriptions. |
| [Implementation Roadmap](ROADMAP.md) | Pending phases per project + ordered implementation with blockers (run `/team-lead:roadmap` to refresh). |
| [System Architecture](ARCHITECTURE.md) | Overall architecture: apps ↔ packages ↔ shared infrastructure + communication layers. |
| [Agents Flow](diagrams/agents/FLOW.md) | Team-lead implementation workflow: plan → backlog → implementation (dev/review/test/PR). |
| [k3s Verification](diagrams/infra/K3S_VERIFICATION.md) | Live test results of the deployed k3s stack. |

---

## 🗺️ Component Diagrams

Each component has two docs:

- **`FLOW.md`** — layered diagram (Presentation/Application/Infrastructure/Domain), key classes, interactions, and data extract→transform→persist.
- **`CLASSES.md`** — exhaustive class map (role, collaborators, data in/out).

### Applications

| Component | Flow | Classes | Type |
| :--- | :--- | :--- | :--- |
| **pole_api** | [FLOW](diagrams/pole_api/FLOW.md) | [CLASSES](diagrams/pole_api/CLASSES.md) | FastAPI backend |
| **pole_fe** | [FLOW](diagrams/pole_fe/FLOW.md) | [CLASSES](diagrams/pole_fe/CLASSES.md) | Angular FE |
| **pole_analyst** | [FLOW](diagrams/pole_analyst/FLOW.md) | [CLASSES](diagrams/pole_analyst/CLASSES.md) | Angular FE |
| **pola_agent** | [FLOW](diagrams/pola_agent/FLOW.md) | [CLASSES](diagrams/pola_agent/CLASSES.md) | Origin project (chatbot host) |

### Packages

| Component | Flow | Classes | Type |
| :--- | :--- | :--- | :--- |
| **pole_ml** | [FLOW](diagrams/pole_ml/FLOW.md) | [CLASSES](diagrams/pole_ml/CLASSES.md) | ML pipeline |
| **pole_tools** | [FLOW](diagrams/pole_tools/FLOW.md) | [CLASSES](diagrams/pole_tools/CLASSES.md) | Reusable tools + CLI |
| **chatbot** | [FLOW](diagrams/chatbot/FLOW.md) | [CLASSES](diagrams/chatbot/CLASSES.md) | Conversational agent |
| **jobs** | [FLOW](diagrams/jobs/FLOW.md) | [CLASSES](diagrams/jobs/CLASSES.md) | Job infrastructure |
| **pole_crop** | [FLOW](diagrams/pole_crop/FLOW.md) | [CLASSES](diagrams/pole_crop/CLASSES.md) | FFmpeg service |
| **pole_crawler** | [FLOW](diagrams/pole_crawler/FLOW.md) | [CLASSES](diagrams/pole_crawler/CLASSES.md) | Instagram crawler |

---

## 🗃️ Plan / Spec Sources (authoritative)

| Project | Plan |
| :--- | :--- |
| pole_api | [`app/pole_api/PLAN.md`](app/pole_api/PLAN.md) |
| pole_analyst | [`app/pole_analyst/PLAN.md`](app/pole_analyst/PLAN.md) + [`fe_design.md`](app/pole_analyst/fe_design.md) |
| pole_fe | [`app/pole_fe/PLAN.md`](app/pole_fe/PLAN.md) |
| pola_agent | [`app/pola_agent/PLAN.md`](app/pola_agent/PLAN.md) |
| keycloak | [`app/keycloak/PLAN.md`](app/keycloak/PLAN.md) |
| infra | [`app/infra/PLAN.md`](app/infra/PLAN.md) |
| pole_ml | [`packages/pole_ml/PLAN.md`](packages/pole_ml/PLAN.md) |
| pole_tools | [`packages/pole_tools/PLAN.md`](packages/pole_tools/PLAN.md) |
| chatbot | [`packages/chatbot/PLAN.md`](packages/chatbot/PLAN.md) |
| jobs | [`packages/jobs/PLAN.md`](packages/jobs/PLAN.md) |
| pole_crop | [`packages/pole_crop/PLAN.md`](packages/pole_crop/PLAN.md) |
| pole_crawler | [`packages/pole_crawler/PLAN.md`](packages/pole_crawler/PLAN.md) |
| infra | [`app/infra/PLAN.md`](app/infra/PLAN.md) |
| keycloak | [`app/keycloak/PLAN.md`](app/keycloak/PLAN.md) |
| dev-ops | [`dev-ops/PLAN.md`](dev-ops/PLAN.md) |
