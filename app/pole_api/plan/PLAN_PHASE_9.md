# Fase 9 — Extraction + Histogram Pipeline — ✅ DONE

> Plan maestro: [PLAN.md](PLAN.md)

## Alcance

- Pipeline de extracción de landmarks + procesamiento de histogramas por métrica (8 métricas).
- Producción de `signal_histograms` (cohort stats) y `skeleton_histograms` (video signals).
- Endpoints de histogramas para el FE.

## Estado

- **DONE** — pipeline extracción+histogramas operativo (commits `cc0af52..e02fb26`).

## Dependencias

- Fases 1-8.

## Criterios de aceptación

- Histogramas por métrica producidos y consultables.

> **Note (refactor posterior):** los nombres `signal_histograms` → `skeleton_cohort_signals` y
> `skeleton_histograms` → `skeleton_video_signals` se realizan en la Fase 15 (rename).