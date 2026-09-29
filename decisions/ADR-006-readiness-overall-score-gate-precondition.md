# ADR-006: Readiness `overall_score` gate precondition — never gate on an unwritten field

> Repo-wide architectural decision record. All ADRs live under `docs/decisions/`.
> Phase detail: `docs/app/pole_api/plan/PLAN_PHASE_42.md`. Evidence tickets:
> `docs/app/pole_api/phase-42-coach-gate-25/PAIML-POLE-API-139.md` (writer gap),
> `docs/app/pole_api/phase-42-coach-gate-25/LOCAL_GATE_20260923_2125.md`
> (local 21/25 baseline).

## Status
Accepted

## Date
2026-09-24

## Context

The SAMPLE-5 break/fix cycle (phase 42, coach 25-battery gate) produced a
failure family that was **not a product regression** but a gate-design error:
the harness required a field nobody wrote.

- **Breaker:** code PR #333 → squash `9984851`
  (`PAIML-POLE-API-137`: harness real-session discovery + fake
  `seed-measurements` revert) introduced a `typeof overall_score === 'number'`
  discovery precondition in `app/pole_analyst/e2e/helpers.ts`.
- **Why it broke:** per `PAIML-POLE-API-139` binding evidence, there were
  **zero writers repo-wide** (`grep overall_score=` empty). Histograms carried
  `scores` / `z_mean` / `phase_scores` but no `overall_score`, so the summary
  join read `$histogram.overall_score` → always `None`. Every histogram scored
  `null` → readiness evidence collapsed to **RE 1/5, `rag_proof: false`**.
- **Fix chain (why each piece was needed, not just what landed):**
  - `7c69e4f` / 139 — the actual writer: worker computes + persists
    `overall_score` as the **plain mean** of metric scores at analysis
    completion, plus a one-shot backfill for already-scored histograms;
    **empty scores → `None`, not `0`** (0 would fake a score where no data
    exists). Live proof: backfill stamped 72.39/68.05 on local histograms.
  - `57fb906` / 134 — tiered readiness contract **T1/T2/T3** + RE-02
    session-resolution fix, so absence of data is a tested tier behavior
    instead of a setup failure.
  - `b614d68` / 136 — deterministic readiness retrieval for RE-04
    (tool-selection nondeterminism cured the same way 125 cured plan/injury).
  - `66a9d83` / 141 — tier-appropriate spec assertions (test-only
    recalibration; RE-05's "matrix has data rows" contradicted the 134 tier
    contract when zero Brass Monkey data exists anywhere).
  - `7ed367f` / 143 + `3e1c081` / 144 — tier-marker emission on
    ReAct-delegated readiness paths (RE-01/RE-04), single source of truth in
    `readiness_tiers`, grounded-only (no fabrication).
- **Staging lesson:** user-confirmed all tests pass locally, but the staging
  fresh gate `20260924-090655` scored **20/25** because the staging image
  (`:develop`) **predated the fix** — pod start 00:48 vs 144 merge 02:27.
  A later fresh run `20260924-094525` scored **21/25**. Artifacts:
  `app/pole_analyst/test-results/coach-150q/<RUN_ID>/` in `pole-ai-ml`.
  The gate compared a **branch name**, not the **image digest** actually
  serving — so it measured stale code and reported it as current failure.

## Decision

**No harness or backend gate may require a field without all three landed
first:**

1. **A writer** — production code that computes + persists the field on the
   live path (not a seed, mock, or fixture).
2. **A backfill** — migration/script covering pre-existing docs that have the
   inputs but lack the field (with explicit empty/absent semantics, e.g.
   empty → `None`, never `0`).
3. **An image-digest check in the run report** — every gate report records
   the serving image digest (and pod start time vs merge time), and FAILs
   closed as "stale image" instead of scoring the battery when the digest
   predates a required fix.

Concretely for this cycle: the `overall_score` numeric-score filter was only
legitimate after `7c69e4f` (writer + backfill) **and** a staging image
containing it; any gate run on an older digest is void, not a product FAIL.

## Alternatives Considered

### Keep gating on branch name (`:develop` tag) only
- Pros: simplest report; no digest plumbing.
- Cons: exactly the observed failure — `:develop` is a floating tag, so a pod
  started before a merge silently tests old code. The 20/25 vs 21/25 delta
  was image age, not product quality.
- Rejected: branch names are intents, digests are facts. Gates score facts.

### Seed the field with synthetic values to make the gate pass
- Pros: unblocks the battery immediately.
- Cons: violates the binding phase-42 user decision (**no mock data**) and
  repeats the rejected 131/137 fake-seed pattern — a green gate that proves
  nothing about real uploads.
- Rejected: the writer must compute from real `scores` on real histograms.

### Relax the harness precondition to accept `null` scores
- Pros: no backend change needed.
- Cons: hides the real gap (unscored sessions undiscoverable) and weakens
  every future numeric filter to "optional" — the gate stops discriminating.
- Rejected: the precondition was correct; the field was missing. Fix the
  writer, not the assertion.

## Consequences

- Harness preconditions on persisted fields now require a **writer + backfill
  + digest** triple before they can gate. Ticket authors check
  `rg "<field>\s*=" app/` for zero-writer gaps the way 139 did.
- Run reports (local `LOCAL_GATE_*` and staging fresh-gate notes) record
  **image digest + pod start vs merge time**; stale-image runs are voided,
  never scored against the product.
- Accepted cost: slightly slower gate setup (digest lookup, backfill run).
  Payoff: no repeat of a full break/fix cycle spent discovering that the gate
  itself was testing code that did not contain the fix.
- Docs lag flagged (order inversion): code PRs #339–#345 (140–145) are merged
  in `pole-ai-ml` while their ticket files still read 📋 PLANNED. This ADR
  records the lesson anyway; ticket-status backfill is out of scope here.
