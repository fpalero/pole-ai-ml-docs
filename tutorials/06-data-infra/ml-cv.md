# Theme 06 — Data Acquisition & Infra · Audience: ML / CV Engineers

> For ML engineers who must also feed the model (data acquisition) and ship it
> (infra). The "you are the whole DevOps team" collection.

## Catalog

### F1 (adapted) — Feeding the Model: Curating a Video Dataset From Instagram
- **Difficulty:** Intermediate
- **Type:** Practical guide
- **Hook:** "Your model is only as good as the data you can scrape, validate, and version."
- **Description:** The `pole_crawler` pipeline: authenticated Instagram sessions
  (CSRF/sessionid cookies), anti-bot waits, DiskWriter + PostMetadata storage,
  and the QC loop (posts into a pending queue, accepted/QC'd before touching the
  model). Includes 429/rate-limit handling and proxies.
- **Grounding:** `docs/packages/pole_crawler/PLAN.md`, `docs/diagrams/pole_crawler/CLASSES.md`, `docs/app/pola_api/flows.md` (UC-20..24).
- **Sellable angle:** "Data acquisition for CV" is a real, underserved pain.

### F2 (ML lens) — Shipping Your Model: Docker → k3s + Helm
- **Difficulty:** Intermediate/Advanced
- **Type:** Deployment guide
- **Hook:** "Model training works on your laptop; making it run forever somewhere else is the job."
- **Description:** The deployment path: docker-compose for local dev
  (Mongo + Redis + Ollama + Keycloak) → k3s production with Helm charts, health
  probes, Traefik ingress, Trivy vulnerability scan, and GH Actions auto-deploy
  per environment (dev/staging/prod with manual gate on prod).
- **Grounding:** `docs/ARCHITECTURE.md` (deployment), `docs/app/infra/PLAN.md`, `docs/app/infra/phase-2-dev-auto-deploy/PAIML-INFRA-005.md`.
- **Sellable angle:** "MLOps for the solo ML dev" — very reachable buyers.