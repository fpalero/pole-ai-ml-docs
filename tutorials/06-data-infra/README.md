# 06 — Data Acquisition & Infrastructure

> Getting the data (Instagram crawler) and running the stack (Docker → k3s +
> Helm, Keycloak identity). Grounded in `packages/pole_crawler/`,
> `infrastracture/`, and `docs/app/infra/`.

## Core articles in this theme

| ID | Title | Difficulty | Primary audience |
| :--- | :--- | :--- | :--- |
| F1 | Scraping Instagram at Scale: Sessions, Anti-Bot & Rate Limits | Intermediate | Backend |
| F2 | From Local Docker to k3s: Deploying an ML Stack with Helm | Intermediate/Advanced | Backend + DevOps |
| F3 | Keycloak as the Identity Layer for an AI Product | Intermediate | Backend |
| F4 | Zero-Dependency FFmpeg Primitives | Intermediate | Backend + ML/CV |
| F5 | Durable Jobs: Mongo Authority, Redis Signal | Advanced | Backend |
| F6 | CI Security for Small Teams: Trivy, Env-Gated Deploys, Slack | Intermediate | Backend + DevOps |
| F7 | Self-Hosted OpenAI-Compatible LLM Routing | Intermediate/Advanced | Backend + PM |
| F8 | Magic Links & Temp Access: Identity for a Consumer Product | Intermediate | Backend |
| F9 | Distributed Logging on a Budget: Filebeat to ElasticSearch | Intermediate/Advanced | Backend + DevOps |
| F10 | Branding Keycloak: Vanilla Login to On-Brand Realm | Intermediate | Frontend + DevOps |

## What makes this theme sellable

- **F1** covers authenticated sessions, CSRF/sessionid cookies, anti-bot waits,
  and 429 handling — gritty, high-search, and rarely written about honestly.
- **F2** is a complete local-dev → production path (docker-compose with
  Mongo/Redis/Ollama/Keycloak → k3s + Helm, health probes, Traefik, Trivy,
  GitHub Actions auto-deploy per env).
- **F3** documents real Keycloak gotchas (realm-as-source-of-truth, the
  "ConfigMap change doesn't roll the pod" checksum fix, magic-link auth), which
  is exactly the material teams search for.

## Source docs

- `docs/packages/pole_crawler/PLAN.md`, `docs/diagrams/pole_crawler/CLASSES.md`
- `docs/app/infra/PLAN.md`, `docs/app/infra/phase-2-dev-auto-deploy/PAIML-INFRA-00x`
- `docs/app/keycloak/phase-7-magic-link-fix/PAIML-KEYCLOAK-015.md`
- `docs/ARCHITECTURE.md` (deployment architecture)

---

## Docs per audience

- [`ml-cv.md`](ml-cv.md) — ML / computer vision engineers
- [`fullstack-backend.md`](fullstack-backend.md) — full-stack / backend engineers
- [`junior-mixed.md`](junior-mixed.md) — mixed beginner → intermediate
- [`tech-entrepreneur.md`](tech-entrepreneur.md) — entrepreneur / technical PM