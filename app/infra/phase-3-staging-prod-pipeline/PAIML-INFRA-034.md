# Ticket: PAIML-INFRA-034

## Title
[CI] Pin KUBECONFIG to runner-owned config in deploy workflows

## Description
`deploy-dev` / `deploy-staging` / `deploy-prod` write the decoded `KUBE_CONFIG` secret to `$HOME/.kube/config`, but on the self-hosted runner (`ipsf-server`, k3s single node) the `KUBECONFIG` env var points at `/etc/rancher/k3s/k3s.yaml` (root-owned). Every `kubectl` call therefore ignores `$HOME/.kube/config`: the 033 rename dies on `open /etc/rancher/k3s/k3s.yaml.lock: permission denied` (masked by `|| true`) and the next step's bare `use-context ipsf-server` fails hard. Seen live on run 35927554255 (2026-09-23, post-#45): `error: open /etc/rancher/k3s/k3s.yaml.lock: permission denied` followed by `error: no context exists with the name: "ipsf-server"`. Fix by exporting `KUBECONFIG` to the runner-owned file for all subsequent steps.

## Repository
`pole-ai-ml-infra`

## Affected
- `.github/workflows/deploy-dev.yml` (kubeconfig setup step)
- `.github/workflows/deploy-staging.yml` (kubeconfig setup step)
- `.github/workflows/deploy-prod.yml` (kubeconfig setup step)

## What to Do (Implementation Steps)
- [ ] Step 1: In each workflow's kubeconfig setup step, after writing `$HOME/.kube/config` (and before/after the 033 rename logic), add `echo "KUBECONFIG=$HOME/.kube/config" >> $GITHUB_ENV`
- [ ] Step 2: Keep the 033 tolerant rename/use-context logic as-is; do not revert it
- [ ] Step 3: No secrets committed; no other step logic changed
- [ ] Step 4: `actionlint` clean on all 3 workflows

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `actionlint` clean on all 3 workflows
- [ ] Live deploy run green (no `k3s.yaml.lock` permission error, no `no context exists` error)
- [ ] All subsequent `kubectl`/`helm` steps in the job use the runner-owned `$HOME/.kube/config`
- [ ] No secrets committed

## Dependencies
- **Blocks:** None
- **Blocked By:** None
- **Related:** PAIML-INFRA-033, PAIML-INFRA-008, PAIML-INFRA-010