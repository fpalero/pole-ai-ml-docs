# Project Variables: infra

## Ticket Counter
- **Last ticket number**: 36

> Anomaly note (docs-unified): incoming `feature/PAIML-POLE-RAG-037-INFRA-026-docs` counter was 26 (older); superseded, MAX 28 kept (026 + 037 files already present via develop).
> Docs-unified: incoming `feature/PAIML-INFRA-028-traefik-ws-timeout` counter was also 28 (same); no collision, notes kept (028 file lands via this merge).
> Docs-unified: incoming `docs/PAIML-INFRA-025-deploy-develop-checkout` counter was 25 (older); superseded, MAX 28 kept (025 file lands via this merge).
> 2026-09-23: PAIML-INFRA-029 exists in phase-2-dev-auto-deploy/ (counter was stale at 28); 030 created (phase-3-staging-prod-pipeline/PAIML-INFRA-030.md).
> 2026-09-23: 031 created (phase-3-staging-prod-pipeline/PAIML-INFRA-031.md) — supersedes 030 (030 stays CLOSED/superseded).
> 2026-09-23: 032 created (phase-3-staging-prod-pipeline/PAIML-INFRA-032.md) — pole-api memory limit 8Gi → 16Gi staging overlay (values-dev.yaml).
> 2026-09-23: 033 created (phase-3-staging-prod-pipeline/PAIML-INFRA-033.md) — kubeconfig context hardening (PR #45).
> 2026-09-23: 034 created (phase-3-staging-prod-pipeline/PAIML-INFRA-034.md) — pin KUBECONFIG to runner-owned file (root cause: runner KUBECONFIG points at /etc/rancher/k3s/k3s.yaml).
> 2026-09-23: 035 created (phase-3-staging-prod-pipeline/PAIML-INFRA-035.md) — checksum annotation so env configmap change triggers FE/analyst rollout (subPath no hot-reload).
> 2026-09-24: 036 created (phase-3-staging-prod-pipeline/PAIML-INFRA-036.md) — feClientRedirects leak in values-dev + realm re-import on deploy (live realm still had pole-ml/pole-coach).
