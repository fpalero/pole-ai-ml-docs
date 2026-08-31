# Fase 12 — Frame-detection Summary endpoint — 📋 PLANNED

> Plan maestro: [PLAN.md](PLAN.md)

## Contexto

Endpoint de detección de frames/segmentos del truco a partir de los landmarks del video: computa
detecciones por métrica (puntos donde `|z| > 1`), el `critical_frame`/`critical_phase`/`critical_metric`
y el summary de análisis.

## Alcance detallado

- **Feature Context:** `pole_fe` (Biomechanical Signal Analysis) y `pole_analyst` (Summary tab)
  necesitan la detección de frames/segmentos de un video.
- **Componente(s):** `app/pola_api/api/analysis` (o `tools/histograms/summary`), detector de
  critical frames.

### Entrada / Salida

- Entrada: doc `skeleton_histograms` (o recomputar sobre landmarks).
- Salida: summary con `z_mean` por métrica, `scores` 0-100, `detections[]` (frames con
  `metric`, `phase`, `z`, `frame_image_path`), `critical_frame`, `critical_phase`,
  `critical_metric`, `phases` detectadas + `confidence`.

### Estado

- **PLANNED** (detalle completo en el PLAN.md original §9).

## Dependencias

- Fase 11 (histogram analysis).

## Criterios de aceptación

- Summary endpoint devuelve detecciones + critical frame/phase/metric.