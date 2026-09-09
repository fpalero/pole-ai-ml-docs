# Article Catalog — by Topic

All articles are grounded in real, working code from the `pole-ai` project.
Grouped by topic; each entry has a title and a short description.

---

## 1. Skeleton Extraction & Pose Processing

- **Production-Grade Pose Extraction with MediaPipe** — Build a production pose pipeline with MediaPipe Pose in VIDEO mode: frame-by-frame landmark capture, hip-center plus shoulder-width normalization for translation and scale invariance, and visibility filtering. Real SkeletonExtractor pattern; leaves you with classifier-ready vectors.

- **The "Monotonically Increasing Timestamp" Bug** — MediaPipe crashed with "Input timestamp must be monotonically increasing". A real production bug story: reusing one extractor instance across files breaks VIDEO mode. Teaches reset() lifecycle discipline and per-video extractor instances.

- **From Video to Vectors: Biomechanical Feature Engineering** — Turn normalized landmark time-series into per-frame biomechanical features—joint angles and speeds—feeding 30×14 sliding windows and 8-signal histogram metrics resampled to 100 points per phase. Evidence that hand-crafted features win on small datasets.

- **Sliding Windows, Data Augmentation & Small Datasets** — A small-data playbook: 30-frame sliding windows with stride 5, mirror/timing/perturbation augmentation, class weights, and Chroma-based oversampling as few-shot assist for new classes. The "200 videos done right" beats "10k videos done wrong" argument.

- **Automatic Phase Detection in Sports Video** — Segment a trick automatically: entrance, execution, exit. How reference data and metric time-series drive phase detection without manual frame marking, plus the failure modes when phases drift. From the handspring feature.

- **8-Signal Histogram Analysis & Cohort Z-Scores** — Two-pass shape analysis: resample each trick to 300 points (100 per phase), aggregate a cohort mean/std, then score every athlete against it with z-scores (0-100) and auto-extract critical-frame JPEGs at |z|>1. Reading "shape" instead of raw frames.

---

## 2. TensorFlow & Model Architecture

- **Sequence-to-Vector: LSTM that Outputs Embeddings, Not Just Classes** — One LSTM forward pass yields both classification logits and a 128-dimensional bottleneck embedding. Two jobs, one model: classify and power similarity search. Covers architecture, input contract, and why dual output beats training two models.

- **Defensive Training: Leave-One-Out + Categorical Crossentropy** — Honest evaluation on tiny labeled datasets: Leave-One-Out splits, early stopping, learning-rate scheduling, and per-class metrics as a release gate. Teaches how to avoid fooling yourself with a single accuracy number.

- **The Hybrid Classifier Pattern: Neural Net + Vector Search Fallback** — The signature pattern: LSTM classifies first; below a 0.7 confidence threshold a ChromaDB nearest-neighbor fallback rescues low-confidence and novel classes. Improves accuracy, handles unseen tricks, and is immediately reusable.

- **Model Persistence, Versioning & the Retraining Toolkit** — MLOps for a one-dev team: .keras/SavedModel persistence with metadata, and the retraining routes compared—fine-tune existing, few-shot assist, threshold steering. Version your model like a data artifact.

- **Exporting to the Browser: TensorFlow.js + int8 Quantization** — Convert the LSTM to TensorFlow.js with int8 quantization: payload under 2 MB, sub-30 ms inference on WebGL. Covers versioning by run_id and rebuilding the exact training-time input window in the browser.

- **From Recognition to Action: VideoCutter with Confidence History & Debounce** — Turn per-frame predictions into clean clips: confidence history, dual LSTM+Chroma thresholds, debounce, transition filtering, region reconstruction, and lossless ffmpeg extraction. The bridge from classifier output to shipped feature.

- **CLI-First ML Pipeline: Eight Commands, One Workflow** — process-data, train-model, process-embeddings, evaluate-video, find-by-similarity, audit-clips, samples-info, crop-trick. Why a rock-solid CLI beats a GUI for reproducible model work—and how the same services mount behind an API later.

- **Testing an ML Pipeline Honestly** — Beyond model accuracy: fakeredis and mongomock substitute external stores, .keras pipelines get stubbed, integration suites skip heavy training, and an 80% coverage gate keeps it honest. Keeping a data pipeline testable when every stage talks to infrastructure.

- **Human-in-the-Loop Model Promotion** — Turn scraped data into a training set with a human gate: per-video selected_for_training flags, readiness stats, train vs fine-tune window selection, then approve/activate to make a run live. Why the deploy step is a human decision, not an API call.

---

## 3. Embeddings & Vector Search

- **ChromaDB in Practice: k-NN Voting & the Config-Bug Case Study** — 128-d embeddings stored in ChromaDB with cosine search and k-NN voting. Carries a real cautionary tale: components pointing at different persist dirs and collection names silently losing data. Teaches canonical config and idempotent indexing.

- **Retrieval-Augmented Recognition: Nearest-Neighbor Fallback** — ChromaClassifier k-NN voting with confidence, plugged under the hybrid pattern as the LSTM fallback. Covers cosine-distance thresholds, metadata hygiene, and ranked matches—a few-shot-friendly classifier when novelty is the norm.

---

## 4. RAG & Retrieval Systems

- **Zero-Cost Offline Documentation RAG** — A free, offline RAG: local all-MiniLM-L6-v2 embeddings, ChromaDB persistence, incremental hash-manifest writes versus full rebuilds, and per-chunk metadata. Reproducible retrieval with zero API cost—the economic alternative everyone asks for.

- **Language-Aware Code Splitting Without tree-sitter** — Why generic splitting mangles code, and a dependency-light splitter using code-specific separators and source-suffix selection that skips node_modules, builds, and lockfiles. The tree-sitter-free alternative for teams that can't ship native deps.

- **Multimodal RAG with Image Descriptions** — Two collections, one store: text chunks and image descriptions embedded side by side in ChromaDB. Readers query by meaning across documents and figures, with full-rebuild semantics. Retrieval that understands pictures, not just prose.

- **Replacing Marker/Surya with PyMuPDF: Know Your Corpus First** — A PDF-heavy RAG was hanging on multi-GB Surya OCR weights plus GPU image captions. A five-minute corpus scan showed every PDF has embedded text—so PyMuPDF swapped in and the heavy lane died. Dependency diets start with data, not tools.

---

## 5. Real-Time Systems & Full-Stack ML

- **Real-Time Recognition: WebSockets, Circular Buffers & Vote Consensus** — Live recognition under a 100 ms budget: 30-frame circular buffer stepped at stride 5, 3/5 vote consensus, cosine checks, and WebSocket delivery. Interleaving frames, inference, and I/O without breaking latency.

- **Wrapping ML in an Agent: ReAct Loop + Tool Registry** — A bounded ReAct agent exposing ML capabilities: sync tools for histogram and similarity, job-mode tools for crop and shift, plus rate limiting and error capture. Marshal long-running ML operations safely through an LLM agent.

- **Coaching Feedback from Metrics: Z-Score Outliers + LLM** — AI coaching from metrics: z-score outliers against a cohort flag flaws, critical-frame images and deviation plots attach, and an LLM writes contextual tips plus 4-week improvement plans. The Dartfish/Hudl idea built open-source.

- **Taking an Agent to Production: Sessions, Rate Limits & Metrics** — The layer between a working agent and a dependable product: session schema, Redis and Postgres repositories with read-through caching, sliding-window rate limiting, and metrics on tool latency and LLM tokens.

- **Custom ReAct vs LangGraph: Two Ways to Build the Same Agent** — One challenge—"analyze this video"—implemented twice: a hand-rolled ReAct loop versus a StateGraph with conditional routing. Trade-offs, token accounting, and where the framework earns its keep.

- **Design Tokens → Real UI: An AI-Generated Angular Frontend** — Take a token-driven design system into an Angular app: lazy-loaded features, signal-based state, chart components, and a resilient WebSocket chat UI. How design-system discipline keeps AI-generated screens consistent.

- **Feature-Sliced FastAPI: Structure That Never Outgrows You** — A backend organized by slices (crawler, training, video, tools) over one shared core, plus an async job pattern where every long op returns 202 + job_id. Why feature slices with shared state beat sprawling routers, and how to mount the same package as app or slice.

- **The 'No Class States' Refactor: Deriving State from Data** — Remove the class status machine and validate by related entities instead: a video is 'ready to train' when its windows exist and are flagged, not because a status field says so. A case study in letting the data be the state machine.

- **Deterministic Guardrails for LLM Agents** — Rules your agent can't talk its way around: word-matched confirmation (never an LLM judgment), tool-call gating on session state, off-script recovery with a rephrase budget, and a synthetic session-state block injected per turn. Safety that survives prompt drift.

- **Model Registry UI: The Human Gate for ML Deploys** — A registry screen where runs are rows to review, compare, and promote: live epoch progress, per-class metrics, a two-run comparison matrix, and approve/activate that flips the active pointer. The UI that makes human-in-the-loop model promotion actually work.

- **Training Studio: Launching Long ML Jobs From a Browser** — Turn train/fine-tune into a form: radio mode cards, multi-class checkboxes with per-class video counts, data-balance warnings, and confirm dialogs that set expectations ('may take hours') before epoch progress streams live. UX for a job launcher.

---

## 6. Data Acquisition & Infrastructure

- **Scraping Instagram at Scale: Sessions, Anti-Bot & Rate Limits** — Authenticated sessions with CSRF and sessionid cookies, anti-bot waits, DiskWriter persistence, and a QC loop that keeps scraped posts safe before use. How to survive 429 rate limits and session rot.

- **From Local Docker to k3s: Deploying an ML Stack with Helm** — The full deployment path: docker-compose for local dev, then k3s with Helm charts, health probes, Traefik ingress, Trivy scans, and GitHub Actions deploying per environment. One recipe for the solo ML dev.

- **Keycloak as the Identity Layer for an AI Product** — Keycloak done right: realm JSON and themes in the repo as source of truth, magic-link auth, temp-access sessions, and the ConfigMap trap fixed with a checksum annotation. Copyable answers to real Keycloak pain.

- **Zero-Dependency FFmpeg Primitives** — A stdlib-only wrapper that shells out to ffmpeg/ffprobe: frame-accurate re-encode crops, keyframe-aligned stream copies, duration/metadata probes, and 320px thumbnails. The reusable primitive behind every crop, shift, and preview.

- **Durable Jobs: Mongo Authority, Redis Signal** — Job infrastructure done right: authoritative state in Mongo, Redis as a FIFO of ids plus pub/sub events; exponential backoff retries, cooperative cancellation, and WebSocket progress relay. Why the queue should never be your source of truth.

- **CI Security for Small Teams: Trivy, Env-Gated Deploys, Slack** — Security as a pipeline stage: image vulnerability scanning, environment protection (dev auto, staging manual, prod gated), and deployment notifications. A reasonable security posture without a dedicated security engineer.

- **Self-Hosted OpenAI-Compatible LLM Routing** — Run your own model router for CI and internal tools: two auth tiers, runtime API-key provisioning, keyless mode for ephemeral jobs. Keep prompt traffic in-house and cut per-call cost with an OpenAI-compatible /v1 surface.

- **Magic Links & Temp Access: Identity for a Consumer Product** — Keycloak for end users, not just employees: SMTP verify-email magic links with a dev Mailpit sandbox, short-lived temp-access sessions, a GDPR data purge, and credential separation via Helm secrets. Consumer-grade auth that scales down to one developer.

- **Distributed Logging on a Budget: Filebeat to ElasticSearch** — Centralize logs for an ML stack without a splunk-sized bill: single-node Elasticsearch via Helm on k3s, Filebeat shipping app and package logs, index-lifecycle management, and green/yellow health as the acceptance gate. Observability that fits on one node.

- **Branding Keycloak: Vanilla Login to On-Brand Realm** — Keycloak themes as source of truth: FreeMarker page templates, a full visual restyle from shared design tokens, and realm settings shipped together in the infra repo. Making your identity pages feel like product, not a default.

---

## 7. The "Meta" Content: Process & Engineering Systems

- **Documentation-Driven Development: PLAN → Tickets → RAG** — Plan-first workflow: PLAN.md, per-phase plans, tickets with acceptance criteria and effort, then a docs RAG for retrieval. Documentation as steering wheel rather than post-hoc report. Every feature stays traceable and queryable.

- **The Crew: LLM Agents Implementing Your Own Tickets** — Bleeding-edge agentic coding: team-lead plan to backlog to implementation, orchestrating developer, reviewer, and tester agents. Covers the LLM provider factory, ticket lifecycle state, and per-ticket repo routing.

- **Multi-Repo Architecture Without Monorepo Pain** — Code, docs, and infra in separate repos with an absolute path-to-repo routing table, worktree feature branches, and develop/main policies. Rules that keep repo splitting from becoming chaos, for mid-size teams.

- **Why Your Project Needs ADRs (Decision Records)** — The decision-record discipline via real examples: ADR templates, the decisions tree as institutional memory, and how records become onboarding material and agent fodder. Six months later you'll still know why.

- **Guardrails for Autonomous Coding Agents** — Before agents can implement tickets, you need rails: bounded executions, policy checks, small-step PR gates, and decision records that say why. The safety layer that lets an agent crew ship without full supervision.

- **AI-Generated UI at Feature Scale: Tabs, Sidebars, Modals** — When the product IS the frontend and AI generates the screens, orchestration is the hard part: phase-by-phase shell, tab/sidebar navigation, detail modals, upload progress panels, and parity across generated views. Keeping AI-produced UI coherent feature after feature.