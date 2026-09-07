# Fase 26 — FE media auth (`?token=` en todos los bindings `<img>`/`<video>`) — 📋 PLANNED

> Plan maestro: [PLAN.md](../PLAN.md) · Backend requerido: ninguno (cero cambios —
> `pole_api` ya soporta `?token=` vía `get_media_claims`, `app/pole_api/src/core/auth.py:290-303`).
> Origen: user-reported defect verificado en staging por live probe (2026-09-07).

## Contexto

Las URLs de imagen/media del FE se rinden sin auth mientras el backend la exige:
`GET /api/analyst-artifacts/histogram_frames/<vid>/frame_0.jpg` → **401 sin token**,
**200 image/jpeg con `?token=<Keycloak access token>`**. El contrato backend
(`get_media_claims`) soporta explícitamente `?token=` para `<img>`/`<video>`
(los navegadores no pueden fijar `Authorization` ahí).

El FE ya tiene helpers con token (`ApiClientService.streamUrl()` que añade
`?token=`, `VideosService.thumbnailUrl()/streamUrl()` vía `appendMediaToken`) y
varios bindings ya los usan (`video-card`, `video-preview`, `analysis-history-table`
vía `thumbnailSrc()` → `videosService.thumbnailUrl()`). Pero los bindings del
chat y de pose rinden URLs raw sin pasar por el helper — esos `<img>` cargan
401 en staging y se ven rotos.

## Tickets

| Ticket | Scope | Estado |
| :--- | :--- | :--- |
| `PAIML-POLE-ANALYST-076` | Helper central `withMediaToken(url)` + aplicarlo en TODOS los bindings media; retry-once-with-fresh-token en `error` de `<img>` (stale-token edge: tokens ~5min vs Cache-Control artefactos 24h); specs + auditoría grep | 📋 PLANNED |
| `PAIML-POLE-ANALYST-077` | Tool-chip artifact links (`extract_frames` + siblings): render REAL tokenized URLs vía helper 076 `withMediaToken` + retry-once (mismo transporte que `.rag-image-card`); fallback a texto plano sin href si el href tokenizado no es feasible — nunca el literal `[artifact]`; resolver la redacción server-side desde el tool result; specs del chip (href tokenizado, retry-once-then-placeholder en 401, cero `[artifact]` en chips) | 📋 PLANNED |

## Tasks

1. **Helper central** — `withMediaToken(url)` (lee el Keycloak access token;
   no-op para `data:`/blob/URLs ya firmadas); reusar `appendMediaToken` /
   `ApiClientService.streamUrl()` si ya cubren el caso — un solo path, sin
   duplicar.
2. **Aplicar en cada binding** — ver auditoría completa en el ticket (076):
   chat `image` (`block.src`), chat `video_segment` thumbnail
   (`block.thumbnail_url`), pose-gallery (×2 `frame_image_path`), pose-insight-list-item,
   annotated-frame `src()`, y cualquier otro `<img>`/`<video>`/`poster` que el
   grep encuentre.
3. **Retry-once-with-fresh-token** — en `(error)` del `<img>`: refrescar token
   y reintentar UNA vez antes del placeholder degradado (mata el stale-token
   edge: token ~5min vs artefacto cacheado 24h).
4. **Specs** — `src` renderizados contienen `token=`; specs del retry-once;
   ≥ 80% cobertura del helper.
5. **Checks** — `npx ng test --watch=false` verde, `lint` limpio, `build`
   typecheck OK.

## Acceptance

- Staging probe: el mismo par curl de la evidencia (401 sin token / 200 con
  `?token=`) + spot check visual: chat `image` y `video_segment` thumbnails
  cargan autenticados.
- Unit tests asertan presencia de token en los `src` renderizados.
- Ningún binding media sin auth (auditoría grep en el ticket, repetible).
- Cero cambios backend.

## Dependencies

- **Blocks:** None.
- **Blocked By:** None (FE-only; backend ya soporta `?token=`).
