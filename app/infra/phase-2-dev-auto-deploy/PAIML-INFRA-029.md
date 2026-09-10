# Ticket: PAIML-INFRA-029

## Title
[CI] Run build-push jobs on self-hosted runners (billing bypass)

## Description
**ROOT CAUSE (billing wall):** GitHub refused to START all jobs in
`pole-ai-ml` `.github/workflows/build-push.yml` — every job died in ~4s
with zero steps executed, cause `billing: failed payments / spending
limit`. Observed 2026-09-09 on build `53eebe4`: 3 identical 4s
zero-step deaths (jobs `base`, `build-and-push`, `deploy-dev` — none
started, no logs beyond the billing refusal). No code or workflow syntax
fault; the GitHub-hosted (`ubuntu-latest`) compute quota is blocked.

**FIX (implemented in parallel, `pole-ai-ml` branch
`feature/PAIML-INFRA-029-selfhosted-runners`):** move all three jobs in
`build-push.yml` from `runs-on: ubuntu-latest` to
`runs-on: [self-hosted, Linux, X64]`:
- `base`
- `build-and-push`
- `deploy-dev`

Target runners `pole-ml-ai-1` + `vmd196736` were online/idle at the time
of the change.

**RISK — unverified runner capability:** Docker / Buildx / git-lfs /
free disk on those boxes is UNVERIFIED. The first post-merge build
doubles as the capability probe: failures from here on will be real
visible errors (missing daemon, Buildx, LFS, disk pressure) — not
billing walls. Record the probe outcome on this ticket.

## Repository
pole-ai-ml (`.github/workflows/build-push.yml` only — no chart change)

## Affected Components
- `pole-ai-ml` `.github/workflows/build-push.yml`
  - job `base`: `runs-on: ubuntu-latest` → `[self-hosted, Linux, X64]`
  - job `build-and-push`: `runs-on: ubuntu-latest` → `[self-hosted, Linux, X64]`
  - job `deploy-dev`: `runs-on: ubuntu-latest` → `[self-hosted, Linux, X64]`
- Self-hosted runners: `pole-ml-ai-1`, `vmd196736` (labels `self-hosted, Linux, X64`)

## What to Do (Implementation Steps)
- [x] Step 1: In `build-push.yml`, set `runs-on: [self-hosted, Linux, X64]`
      on jobs `base`, `build-and-push`, `deploy-dev` (branch
      `feature/PAIML-INFRA-029-selfhosted-runners`).
- [ ] Step 2: Merge to `develop`; confirm the post-merge build-push run
      is picked up by a self-hosted runner (not GitHub-hosted) and all
      three jobs START (no 4s zero-step billing death).
- [ ] Step 3: Capability probe — confirm Docker + Buildx + git-lfs work
      on the runner and free disk suffices; record versions/limits on
      this ticket. Any failure here is a real environment error — fix
      forward on the runner (install Buildx/LFS, free disk) rather than
      reverting unless the box is unusable.
- [ ] Step 4: Confirm the loop still closes: image published to GHCR
      (branch + short-sha tags) and `deploy-dev` dispatch fires toward
      `pole-ai-ml-infra`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Post-merge build-push run executes on a self-hosted runner
      (`pole-ml-ai-1` or `vmd196736`) — all three jobs start, no billing
      refusal.
- [ ] Build publishes the image to GHCR (branch tag + short-sha tag,
      per INFRA-027 contract).
- [ ] `deploy-dev` dispatch fires (repository_dispatch to
      `pole-ai-ml-infra` carries the tag).
- [ ] Probe outcome recorded: Docker/Buildx/git-lfs versions + disk headroom.

## Integration Tests to Run (Local / Staging Verification)
- [ ] `actionlint` clean on `build-push.yml`.
- [ ] Post-merge run inspection: runner name labels self-hosted, job
      durations >> 4s, steps actually execute.
- [ ] GHCR check: dispatched short-sha tag present on the built image.
- [ ] Infra side: `pole-ai-ml-infra` Deploy-to-DEV run triggered via
      `repository_dispatch` (no manual rollout).

## Rollback
Revert the three `runs-on` lines to `ubuntu-latest`. Note: rollback
re-exposes the billing wall — GitHub-hosted jobs will again die in ~4s
until the spending-limit / failed-payment state is cleared. Prefer
fixing the runner forward.

## Dependencies
- **Blocks:** — (unblocks all `develop`-merge builds while billing is red)
- **Blocked By:** PAIML-INFRA-027 (sha-tag contract this ticket must preserve)

## Estimated Effort
- [XS] (Very Small — 3-line workflow change + post-merge probe)
