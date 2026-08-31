# Fase 6 — Video slice — Cut + Review + Shift + Thumbnails — ✅ DONE

> Plan maestro: [PLAN.md](PLAN.md)

## Alcance

- `POST /api/video/classes/{id}/cut` (crop AI con `cutter_override`), `POST /api/video/clips/{id}/review`.
- `POST /api/video/clips/{id}/shift` (reubicar ventana), `GET /api/video/clips/{id}/thumbnail`.
- Cut con `chroma_only` flag, `clips` tab.

## Estado

- **DONE** — cut/review/shift/thumbnails operativos.

## Dependencias

- Fases 1-5.

## Criterios de aceptación

- Cut → review → shift → thumbnails probados.