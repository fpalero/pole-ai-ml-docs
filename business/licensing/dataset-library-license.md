# L2 — Named-Trick Dataset / Kernel Library License

> Type: `licensing/` · data/licensing (B2B) · Priority ⭐

## Description

**The idea in plain English.**
We've spent years collecting and processing pole movement data. We sell that
data — the analyzed skeletons, movement features, and the digital "fingerprint"
of each trick — as a licensed package, so other companies and researchers can
build their own movement-analysis products without spending years collecting
data.

**How it makes money.**
One-off license with a yearly refresh option:

- Landmarks + features (50 tricks): €500–1,500.
- Ready-to-use trick library: €1,500–3,000.
- Full bundle + yearly updates: €3,000–5,000/year.

**Target public.**
Sports-tech companies, app developers, and AI researchers who need real
movement data to train their own models. (Requires clean data rights on every
video before selling — see the caution in the full doc.)

## What it is

Sell a **licensed dataset**: normalized landmark sequences, the per-frame
biomechanical features (angles/speeds), and trick embeddings (LSTM bottleneck +
Chroma) as a packaged, documented artifact that other apps/researchers buy to
bootstrap their own analysis without collecting their own data.

## How it makes money

One-off license fees with attribution restrictions; add a maintenance tier for
re-fresh releases (new tricks, more athletes).

## Subscription or per-service?

**One-off license** (perpetual or 1-yr), with an optional refresh subscription.

| Offering | Price |
| :--- | :--- |
| Landmarks + features (raw, 50 tricks) | €500–1,500 |
| Embedding library + Chroma index (trainable) | €1,500–3,000 |
| Full bundle + refresh subscription (annual) | €3,000–5,000 /yr |

## Implementation

**Surface: data engineering** — export pipelines + licensing/delivery. No new ML.

**Already built (reuse):**
- `pole_tools.process_data` — normalized landmarks/windows (the core artifact).
- `pole_tools.process_embeddings` — embedding/Chroma generation and `manifest.json`.
- Mongo storage + cohort/histogram stats as value-add columns.
- `pole_tools.audit_clips` / `samples_info` for QC of the shipped set.

**Must add (gaps):**
- Export/catalog tool (schema, versioning, checksums, sample splits).
- **Data-rights legal work** — every video/athlete in the set must be licensed for
  redistribution (the crawler is Instagram-derived; verify provenance first).
- Anonymization (no athlete identity in shipped landmarks) + GDPR compliance.
- Licensing/payment + delivery (signed URL / package registry).

## Effort & priority

**Effort: Medium-High** (the data-legal part, not the code).
**Priority: ⭐** — real money early on, but depends on data-rights being clean;
treat as opportunistic rather than a pillar.

*See also: `docs/packages/pole_tools/PLAN.md`, `docs/packages/pole_ml/PLAN.md`,
`docs/packages/pole_crawler/PLAN.md` (provenance caution).*