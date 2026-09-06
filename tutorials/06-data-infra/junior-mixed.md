# Theme 06 — Data Acquisition & Infra · Audience: Mixed Beginner → Intermediate

> Gentle, achievable wins: a small scraper, a first deploy, and identity
> concepts — with the complexity scaled down.

## Catalog

### F1 (intro) — Your First Web Scraper That Doesn't Get You Banned
- **Difficulty:** Beginner → Intermediate
- **Type:** Tutorial
- **Hook:** "It's not about code — it's about sessions, waits, and not hammering the server."
- **Description:** A beginner scraper built on the crawler's lessons: login
  session reuse, polite delays, metadata-first storage, and handling rate
  limits gracefully. Reader builds a small, respectful scraper that actually works.
- **Grounding:** `docs/diagrams/pole_crawler/CLASSES.md`.
- **Sellable angle:** Approachable entry to a high-interest topic.

### F2 (intro) — Your First Container → Cluster Deploy
- **Difficulty:** Intermediate
- **Type:** Tutorial
- **Hook:** "If docker-compose works, k3s is closer than you think."
- **Description:** Step-by-step: package the app in Docker, run it locally with
  docker-compose, then lift onto a k3s cluster with a minimal Helm chart and a
  health check. Demystifies the jump from laptop to cluster.
- **Grounding:** `docs/app/infra/plan/PLAN_PHASE_1.md`, `docs/ARCHITECTURE.md`.
- **Sellable angle:** Beginner-friendly infra is always in demand.