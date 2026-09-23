# Ticket: PAIML-INFRA-032

## Title
[Helm] Raise pole-api memory limit 8Gi to 16Gi on staging (values-dev overlay)

## Description
`pole-api` OOM risk on staging: chart default limit is 8Gi (`charts/pole-api/values.yaml` lines 24–32 — MediaPipe + TensorFlow extract jobs run several videos in parallel, limit kept well above working set). Idle is low (pole-api pod 404Mi; all pods idle ~1Gi; node vmd196736 measured 2026-09-23 at 6561Mi/27% of 24GB via `kubectl top`), but extract spikes need headroom. User decision: raise cluster workload budget to 16GB for pole-api on staging via `values-dev.yaml` overlay only — local default stays 8Gi.

## Repository
`pole-ai-ml-infra`

## Affected
- `infrastracture/helm/pole-ai/values-dev.yaml` (ADD `pole-api.resources.limits.memory=16Gi` override; optionally bump `pole-api.resources.requests.memory` above 512Mi only with justification in PR — keep requests <= limits)
- No other env file touched (`values.yaml`, `values-local.yaml` unchanged)

## What to Do (Implementation Steps)
- [ ] Step 1: In `values-dev.yaml`, add `pole-api:` resources override with `limits.memory: 16Gi` (keep `requests.memory/cpu` as-is unless justified)
- [ ] Step 2: Render check staging: `helm template ./helm/pole-ai -f helm/pole-ai/values-dev.yaml | rg -A2 "memory:"` — pole-api Deployment shows `16Gi`
- [ ] Step 3: Render check local default unchanged: `helm template ./helm/pole-ai -f helm/pole-ai/values-local.yaml | rg "memory:"` — pole-api still `8Gi` / `512Mi`
- [ ] Step 4: `helm lint ./helm/pole-ai`; confirm `requests <= limits` for pole-api
- [ ] Step 5: Post-deploy verify on staging: `kubectl top node vmd196736` + `kubectl top pod -n pole-ai` — node stays < 24Gi, pod runs without OOMKilled under extract load

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Staging render (`-f values-dev.yaml`) shows pole-api `limits.memory: 16Gi`
- [ ] Local render (`-f values-local.yaml`) still shows `8Gi` (default untouched)
- [ ] `requests <= limits` for pole-api (no invalid resources)
- [ ] No other env file touched; no secrets committed

## Integration Tests to Run (Local Verification)
- [ ] `helm template ./helm/pole-ai -f helm/pole-ai/values-dev.yaml | rg "16Gi"` matches pole-api Deployment limits
- [ ] `helm template ./helm/pole-ai -f helm/pole-ai/values-local.yaml | rg "8Gi"` matches (local unchanged)

## Dependencies
- **Blocks:** None
- **Blocked By:** None
- **Related:** PAIML-INFRA-031 MERGED (provides `values-dev.yaml` this ticket overlays — verified on `origin/develop` 2026-09-23).

## Integration Notes
- Headroom math (2026-09-23): node 24Gi RAM, 6561Mi (27%) used; pole-api 16Gi + ~2Gi others ≈ 18Gi < 24Gi — fits with margin.
- No secrets in scope.
