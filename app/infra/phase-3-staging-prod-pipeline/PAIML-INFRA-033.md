# Ticket: PAIML-INFRA-033

## Title
[CI] Harden kubeconfig context handling in deploy workflows

## Description
`deploy-dev` / `deploy-staging` / `deploy-prod` run `kubectl config use-context ipsf-server`, which fails when the `KUBE_CONFIG` secret holds a fresh `k3s.yaml` whose current context is `default`. Seen live 4x on runs 35925242348 / 35925832851 / 35926385819 (`error: no context exists with the name: "ipsf-server"`). Harden the kubeconfig setup step so it works with either secret variant.

## Repository
`pole-ai-ml-infra`

## Affected
- `.github/workflows/deploy-dev.yml` (kubeconfig setup step)
- `.github/workflows/deploy-staging.yml` (kubeconfig setup step)
- `.github/workflows/deploy-prod.yml` (kubeconfig setup step)

## What to Do (Implementation Steps)
- [ ] Step 1: In each workflow's kubeconfig setup step, after writing `$HOME/.kube/config`, add a tolerant line: if current-context differs from `ipsf-server`, rename it to `ipsf-server`, then `use-context ipsf-server`
- [ ] Step 2: Keep it idempotent for both `default` and `ipsf-server` secrets; guard with `|| true` so `set -e` doesn't trip
- [ ] Step 3: No secrets committed; no other step logic changed
- [ ] Step 4: `actionlint` clean on all 3 workflows

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `actionlint` clean on all 3 workflows
- [ ] Both-context render/simulated test passes (`default` and `ipsf-server` kubeconfigs both reach `use-context ipsf-server`)
- [ ] Deploy green (no `no context exists with the name` error)
- [ ] No secrets committed

## Dependencies
- **Blocks:** None
- **Blocked By:** None
- **Related:** PAIML-INFRA-008, PAIML-INFRA-010
