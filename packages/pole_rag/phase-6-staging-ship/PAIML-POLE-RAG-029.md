# Ticket: PAIML-POLE-RAG-029

## Title
[Ops] Staging wiring + seed-transfer runbook (`/data/rag`, embedder model, `kubectl cp`)

## Description
Phase 6, step 3 of 4. Wire staging to the new RAG home and land the 4 DBs on
the PVC. The Helm release `pole-ai` (deploy `pole-ai-pole-api`, `/data` mount,
`POLE_RAG_DATA_DIR` value) is owned by repo `pole-ai-ml-infra` — all chart
edits happen there. The seed + `kubectl cp` steps are an ops runbook: they run
from a `pole-ai-ml` checkout locally but modify no repo files, only PVC data.

## Repository
pole-ai-ml-infra

## What to Do (Implementation Steps)
- [ ] Step 1 [pole-ai-ml-infra]: In
      `infrastracture/helm/pole-ai/charts/pole-api/templates/configmap.yaml`,
      add `POLE_RAG_DATA_DIR: "/data/rag"` next to the existing `CHROMA_PERSIST_DIR:
      "/data/chroma"` entry (leave `/data/chroma` untouched — the
      `movement_embeddings` store, 7712 entries, video flow). Mirror in values
      if the chart parametrises env (do not hardcode the registry/tag).
- [ ] Step 2 [pole-ai-ml-infra]: Ensure `/data/rag` exists owned by `appuser`
      (extend the `mkdir -p /data/...` + `chown appuser` lines in
      `app/pole_api/docker/base.Dockerfile` — file lives in `pole-ai-ml`, so
      open it as a one-line companion PR/change there — or create the dir via
      an init/container `mkdir -p /data/rag && chown 1000:1000 /data/rag` step
      in `infrastracture/helm/pole-ai/charts/pole-api/templates/deployment.yaml`;
      pick one lane and record it). `securityContext runAsUser: 1000` stays.
- [ ] Step 3 [ops-runbook, no repo change]: Seed locally (fast lane, user
      decision). From the `pole-ai-ml` checkout with cached Marker + Ollama
      `llama3.2-vision` + HF weights, run per resource:
      `pixi run rag-seed -- -i packages/pole_rag/sources/<pole|calisthenics|psicology|biomechanics>
      -o /tmp/rag-staging --name <same>`; verify each with
      `pixi run rag-inspect -- -o /tmp/rag-staging --name <same>` (both
      collections > 0 entries).
- [ ] Step 4 [ops-runbook, no repo change]: Transfer into the staging PVC
      (verified writable as `appuser`). Wait for `kubectl rollout status
      deploy/pole-ai-pole-api` green, then per DB:
      `kubectl cp /tmp/rag-staging/<name> <pod>:/data/rag/<name>` (or via a
      debug pod mounting the same PVC). Re-list with
      `kubectl exec <pod> -- ls -R /data/rag` and confirm
      `chroma.sqlite3` per resource; confirm `/data/chroma` mtime/counts
      unchanged.
- [ ] Step 5 [ops-runbook, record lane]: Embedder model at query time
      (`sentence-transformers/all-MiniLM-L6-v2`, 384-dim). Either (a) baked
      into the base image in ticket 027 — confirm with
      `kubectl exec <pod> -- python -c "from sentence_transformers import
      SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"`
      offline-safe; or (b) `HF_HOME`/`SENTENCE_TRANSFORMERS_HOME=/data/rag/models`
      on the PVC with weights pre-copied. Record which lane was taken in the
      release ticket; do not leave both half-done.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Staging ConfigMap renders `POLE_RAG_DATA_DIR=/data/rag`
      (`helm template` proof); `/data/chroma` entry unchanged.
- [ ] `/data/rag` on the staging pod is writable as `appuser` (uid 1000).
- [ ] `/data/rag/{pole,calisthenics,psicology,biomechanics}/chroma.sqlite3`
      present; per-DB `rag-inspect` counts match the local seed counts.
- [ ] Embedder lane recorded and proven (bake proof or `HF_HOME` + weights on
      PVC).
- [ ] No code change in `pole-ai-ml` except the one-line `mkdir` companion if
      that lane was chosen (recorded explicitly).

## Integration Tests to Run (Local Verification)
- [ ] Pre-copy: local `rag-query -o /tmp/rag-staging --name <each> --query
      "<domain probe>" -k 3` returns 3 hits with `source_document`.
- [ ] Post-copy: same query via `kubectl exec` python one-liner with
      `data_dir=/data/rag` (full tool proof is ticket 030).

## Dependencies
- **Blocks**: PAIML-POLE-RAG-030
- **Blocked By**: PAIML-POLE-RAG-028

## Estimated Effort
- [L]
