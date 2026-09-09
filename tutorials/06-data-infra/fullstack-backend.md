# Theme 06 — Data Acquisition & Infra · Audience: Full-Stack / Backend Engineers

> The backend/DevOps meat: resilient scraping, a complete Helm + k3s path, and
> Keycloak identity done right.

## Catalog

### F1 — Scraping Instagram at Scale: Sessions, Anti-Bot & Rate Limits
- **Difficulty:** Intermediate
- **Type:** Practical guide
- **Hook:** "Welcome to the scraper that survived 429s, proxies, and session rot."
- **Description:** Full `pole_crawler` engineering: `make_session` with CSRF +
  sessionid + `ds_user_id` cookies, `InstagramClient` fetching posts with
  anti-bot waits (min_wait/max_wait), DiskWriter/PostMetadata persistence, and
  the QC flow that keeps scraped data safe before it's used.
- **Grounding:** `docs/packages/pole_crawler/PLAN.md`, `docs/diagrams/pole_crawler/CLASSES.md`, `docs/ENV_VARS.md` (Instagram vars).
- **Sellable angle:** High-search, gritty, honest content.

### F2 — From Local Docker to k3s: Deploying an ML Stack with Helm
- **Difficulty:** Intermediate/Advanced
- **Type:** Deployment guide
- **Hook:** "One deploy script, three environments, no drama."
- **Description:** Local docker-compose (Mongo + Redis + Ollama + Keycloak)
  → k3s with Helm charts (`build-push.sh`/`deploy.sh`/`teardown.sh`), values
  overlays per env, health probes (`/health`), Traefik ingress, Trivy scan, and
  GitHub Envs (dev auto / staging manual / prod gated).
- **Grounding:** `docs/app/infra/plan/PLAN_PHASE_1.md`, `docs/app/infra/phase-2-dev-auto-deploy/PAIML-INFRA-004/005.md`, `docs/ARCHITECTURE.md`.
- **Sellable angle:** Complete, tested recipe — gaps in tutorial land for
  k3s + Helm for ML stacks.

### F3 — Keycloak as the Identity Layer for an AI Product
- **Difficulty:** Intermediate
- **Type:** Guide
- **Hook:** "Realm-as-source-of-truth, magic links, and the ConfigMap trap."
- **Description:** Keycloak setup: realm JSON + themes in the repo (source of
  truth), magic-link auth, temp-access sessions, and the real gotcha — theme/
  realm ConfigMap changes don't roll the pod (fixed via checksum annotation and
  absolute per-env data-endpoints).
- **Grounding:** `docs/app/keycloak/phase-7-magic-link-fix/PAIML-KEYCLOAK-015.md`.
- **Sellable angle:** Keycloak pain is real; the fixes are copyable.

### F4 — Zero-Dependency FFmpeg Primitives
- **Difficulty:** Intermediate
- **Type:** Library/engineering guide
- **Hook:** "FFmpeg is the sharpest tool you'll ever shell out to — wrap it once, correctly."
- **Description:** `pole-crop`: a stdlib-only wrapper over `ffmpeg`/`ffprobe` —
  frame-accurate re-encode crops (accurate seek), keyframe-aligned `-c copy`
  fast paths, duration/metadata probes, and `capture_frame` 320px thumbnails.
  Errors as `CropError`; zero third-party Python deps.
- **Grounding:** `docs/packages/pole_crop/PLAN.md`, consumer services in `pole_tools.services`/`pole_chatbot`.
- **Sellable angle:** Under-documented FFmpeg-pattern content; reusable as the
  primitive behind crop/shift/preview features.

### F5 — Durable Jobs: Mongo Authority, Redis Signal
- **Difficulty:** Advanced
- **Type:** Backend architecture guide
- **Hook:** "Your queue should never be your source of truth."
- **Description:** The `pole-jobs` design: authoritative job state in Mongo,
  Redis used only as a FIFO of ids + pub/sub events; `JobWorker` with
  exponential-backoff retries and cooperative cancellation, `JobOrchestrator`,
  and a FastAPI router with a WebSocket progress relay. Tested with fakeredis
  + mongomock.
- **Grounding:** `docs/packages/jobs/PLAN.md`, `docs/diagrams/jobs/CLASSES.md`, `FLOW.md`.
- **Sellable angle:** Durable-job-system content is high value; Mongo-as-truth +
  Redis-as-signal is a defensible, copyable stance.

### F6 — CI Security for Small Teams: Trivy, Env-Gated Deploys, Slack
- **Difficulty:** Intermediate
- **Type:** DevSecOps guide
- **Hook:** "You can't afford a security engineer — you can afford three pipeline rules."
- **Description:** Security as a pipeline stage: Trivy image vulnerability
  scanning, environment protection (dev auto-deploy, staging manual, prod
  gated), and Slack/notifications on deployments. A proportional posture for a
  small to mid-size team.
- **Grounding:** `docs/app/infra/phase-4-security-notifications/PAIML-INFRA-011.md`, `docs/app/infra/plan/PLAN_PHASE_5.md`.
- **Sellable angle:** DevSecOps without enterprise overhead — underserved niche.

### F7 — Self-Hosted OpenAI-Compatible LLM Routing
- **Difficulty:** Intermediate/Advanced
- **Type:** MLOps/self-hosting guide
- **Hook:** "Keep prompt traffic in-house: your own OpenAI-compatible router for CI and tools."
- **Description:** OmniRoute-based routing: two auth tiers (management vs
  runtime Bearer keys), runtime API-key provisioning, `REQUIRE_API_KEY=false`
  keyless mode for ephemeral CI, and an OpenAI-compatible `/v1/chat/completions`.
  Cuts per-call cost and keeps traffic private.
- **Grounding:** `docs/dev-ops/opencode-omnirouter-api-reference.md`, `docs/decisions/ADR-003-oc-pr-review-opencode-big-pickle.md`.
- **Sellable angle:** Cost-control + privacy story for teams routing LLM traffic.

### F8 — Magic Links & Temp Access: Identity for a Consumer Product
- **Difficulty:** Intermediate
- **Type:** Identity/auth guide
- **Hook:** "Keycloak for end users, not just employees — magic links, temp access, and GDPR."
- **Description:** Consumer-grade Keycloak: SMTP verify-email magic links with a
  dev Mailpit sandbox, short-lived temp-access sessions, a GDPR data-purge
  flow, and credential separation via Helm secrets (never the realm JSON).
  Identity that scales down to a solo dev.
- **Grounding:** `docs/app/keycloak/phase-1-keycloak-realm-theme/PAIML-KEYCLOAK-001.md`,
  `phase-2-temp-access/...005`, `phase-3-data-purge/...008`, `phase-5-brevo-smtp/...013`.
- **Sellable angle:** "Consumer Keycloak" is under-served vs enterprise SSO; the
  mail-trap + temp-access + GDPR trio is concrete and copyable.

### F9 — Distributed Logging on a Budget: Filebeat to ElasticSearch
- **Difficulty:** Intermediate/Advanced
- **Type:** Observability guide
- **Hook:** "Centralize logs for an ML stack without a splunk-sized bill."
- **Description:** Single-node Elasticsearch via Helm on k3s, Filebeat shipping
  app and package logs, index-lifecycle management, and `_cluster/health`
  green/yellow as the acceptance gate. Observability that fits on one node and
  one developer's time budget.
- **Grounding:** `docs/app/infra/phase-6-elastic-stack/PAIML-INFRA-016..018.md`,
  `phase-7-pole-api-logs/...019..021`, `phase-8-packages-logs/...022..024`.
- **Sellable angle:** Small-team observability narrative with real Helm specifics.

### F10 — Branding Keycloak: Vanilla Login to On-Brand Realm
- **Difficulty:** Intermediate
- **Type:** Identity UI/branding guide
- **Hook:** "Your login page is your product's handshake — stop shipping the default."
- **Description:** A production Keycloak theme workflow: FreeMarker templates
  (login, error, idle) living in the infra repo as source of truth, a
  Stitch-iteration visual restyle derived from shared design tokens, and realm
  settings kept separate from credentials via Helm secrets. Identity that looks
  designed, with a review loop that keeps it from rotting.
- **Grounding:** `docs/app/keycloak/phase-1-keycloak-realm-theme/`,
  `phase-6-stitch-login-restyle/`, `fe_UI_design_branding.md`.
- **Sellable angle:** "Keycloak theming" is thin on the web and high-demand;
  the Stitch-design-iteration angle is unique.