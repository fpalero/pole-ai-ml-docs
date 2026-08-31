# Fase 25 — Classify-first pipeline (detección de fases con la clase correcta) — ✅ DONE

> Plan maestro: [PLAN.md](../PLAN.md) · Origen: PO 2026-08-24 — "antes de la detección de fases
> debe correr el clasificador: necesitamos la clase para usar los histogramas correctos"

## Contexto

`AnalyzeWorker` runs Phase detection (stage 3) BEFORE Classification (stage 4). On a fresh upload
(no explicit trick_label) the first detection pass compares against empty/stale references, and the
worker compensates by re-running detection after classification. Requirement: classify FIRST, then
detect phases ONCE using the classified class's reference histograms.

## Tickets

| Ticket | Scope |
| :--- | :--- |
| `PAIML-POLE-API-073` | Reorder worker stages: Extraction → Processing → Classification → Phase detection → Summary. Single detection pass with effective label; remove corrective re-run; preserve manual-bounds authority, job_progress contract (FE ProgressPanel), error isolation, and all UC-C/insights side effects. |

## Quality Gates

- `pixi run test-api` green (worker tests updated to new stage order)
- FE job_progress consumers unaffected (stage NAMES unchanged; only execution ORDER changes —
  verify ProgressPanel renders by key, not index)
