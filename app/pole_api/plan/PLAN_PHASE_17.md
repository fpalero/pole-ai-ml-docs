# Fase 17 — Phase detection (analysis) — 📋 PLANNED

> Plan maestro: [PLAN.md](PLAN.md) · Feature: detección automática de fases (handspring) — backend

## Contexto

Detección automática de las fases **ENTRADA / EJECUCIÓN / SALIDA** de un video mediante histogramas
de referencia + distancia de Bhattacharyya + ventana deslizante + consenso temporal (K=5).

## Alcance

### 1. Detector (`PhaseDetector` en slice `analysis`)

- Input: landmarks normalizados (MediaPipe) del video + referencias
  `skeleton_trick_histograms` para el `trick_label` objetivo.
- Para cada métrica usada (5): computar histograma de la ventana deslizante y distancia de
  Bhattacharyya contra la referencia de cada fase.
- Clasificación de la ventana: fase con máxima similaridad; consenso temporal **`required_matches(K)=5`**
  de `window_size=20` con `stride=5`.
- 300 puntos de secuencia = 100 ENTRANCE + 100 EXECUTION + 100 EXIT (orientación al estimar límites).
- Si la máxima similaridad Bhattacharyya < umbral `> 0.7` → **`DESCONOCIDO`** (el FE abre el modal
  manual).

### 2. Servicio de análisis (`DetectPhasesUseCase`)

- `detect_phases(landmarks, trick_label) → PhaseDetectionResult`:
  `{detected: bool, phases: {ENTRADA:{start,end,confidence}, EJECUCIÓN:{...}, SALIDA:{...}},
  confidence, trick_label}`.
- Integrar en `AnalyzeWorker`: etapa "Phase detection" del job (5 etapas):
  Extraction → Processing → **Phase detection** → Classification & analysis → Summary.
- Progreso del job por etapa; `failed`/`skipped` error-isolated (nunca marca el job `failed` salvo
  video corrupto).

### 3. Clasificación (LSTM stub)

- `ClassifyTrickUseCase` LSTM stub: si el modelo no clasifica (baja confianza) → `trick_label=null`
  → el FE pregunta el nombre del truco.

### 4. Persistencia

- `phase_frames` por video (END/start/end frames) → consumido por `PUT
  /api/training/clips/{video_id}/phase-frames` (manual override) y por el Summary.

## Tickets (candidatos)

- [ ] **PAIML-POLE-API-046** — `PhaseDetector` (Bhattacharyya + ventana deslizante + K=5).
- [ ] **PAIML-POLE-API-047** — `DetectPhasesUseCase` + `PhaseDetectionResult` + edge cases
      (referencia vacía → 422 con lista de métricas faltantes).
- [ ] **PAIML-POLE-API-048** — Integración `AnalyzeWorker` (etapa "Phase detection" + progress
      stages) + persistencia `phase_frames`.
- [ ] **PAIML-POLE-API-049** — `ClassifyTrickUseCase` LSTM stub (trick_label null → flujo manual).

## Dependencias

- Fase 16 (referencias `skeleton_trick_histograms`).
- Reutiliza: `HistogramDataProcessor` (resample/binning), `SkeletonExtractor`.

## Criterios de aceptación

- Detección con K=5 + Bhattacharyya probada sobre landmarks falsos de test.
- Referencia vacía → 422 con métricas faltantes; bajo umbral → `DESCONOCIDO`.
- Worker integra la etapa de detección; SLA < 1 min; one analysis at a time.