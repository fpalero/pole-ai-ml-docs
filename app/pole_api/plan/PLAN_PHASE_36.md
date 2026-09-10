# Fase 36 — free-text trick extraction for progression/readiness — 📋 PLANNED

> Plan maestro: [PLAN.md](../PLAN.md) · Tickets:
> [`phase-36-free-text-trick-extraction/PAIML-POLE-API-112.md`](../phase-36-free-text-trick-extraction/PAIML-POLE-API-112.md) ·
> [`phase-36-free-text-trick-extraction/PAIML-POLE-API-113.md`](../phase-36-free-text-trick-extraction/PAIML-POLE-API-113.md) ·
> [`phase-36-free-text-trick-extraction/PAIML-POLE-API-114.md`](../phase-36-free-text-trick-extraction/PAIML-POLE-API-114.md)
> Origen: analyst chatbot progression turn — free-text trick mention never
> reaches `pole_coach` gating.

## 1. Contexto

Cadena de fallo diagnosticada (no re-investigar):

- `SupergraphAnalystAgent._build_state`
  (`app/pole_api/src/analyst_chatbot/coach_providers.py:742-774`) solo fija
  `trick_name` desde el label del histograma del vídeo. Un turno de texto
  libre como *"I am able to do the handspring. Which other trick can I try
  now?"* produce `trick_name=None`.
- El gating de `pole_coach` `resolve_trick(None)` devuelve `unknown` —
  *"No trick name was provided…"*
  (`packages/pole_coach/src/pole_coach/gating.py:101-110`).
- El grafo de consulta `QUERY_DOMAINS` excluye el catálogo
  (`packages/pole_coach/src/pole_coach/graphs/query.py:48`), así que ni
  siquiera una consulta de progresión bien formada puede apoyarse en las
  transiciones del catálogo.
- El catálogo tiene 447 movimientos; la entrada `handspring` declara 6
  transiciones hacia adelante (*forward transitions*): Inverted-Crucifix,
  Butterfly, Flatline, Hangglider, Iron-X, Gemini.

Caso espejo usuario (bank item #27): *"Analyse my latest handspring video and
tell me what to focus on first"* — caso vídeo+truco (video label tiene
precedencia; la extracción de texto libre solo actúa como fallback cuando el
vídeo no aporta label).

### ADR — WHY faltaba la extracción

`_build_state` se diseñó vídeo-céntrico: el `trick_name` era un atributo del
vídeo (vía histograma), nunca una mención del usuario en texto libre. La
progresión/readiness es el primer flujo donde el truco vive solo en la frase
del usuario — de ahí el `None` sistemático. La decisión de esta fase es
extracción determinista (catálogo como vocabulario) en `_build_state`,
delante del gating, sin tocar `pole_coach`: el coach sigue recibiendo un
`trick_name` resuelto o `None` genuino (ningún truco mencionado en ningún
canal).

## 2. Scope

- **112 (extracción):** extracción determinista de `trick_name` desde texto
  libre en `_build_state` (vocabulario = nombres/alias del catálogo,
  normalización minúsculas + guiones/espacios; precedencia: label del vídeo
  > texto libre > `None`). Sin LLM, sin cambios en `pole_coach`.
- **113 (ruteo):** rutar progresión a catalog-first: `QUERY_DOMAINS` +
  catálogo (transiciones forward) y ejemplo de prompt P4.
- **114 (respuesta):** shaping de respuesta "what next" + cobertura UC
  incluyendo bank #27 (caso vídeo+truco con precedencia del label).
- **Fuera de scope:** cambios en `gating.py`, reentrenos, trabajo FE,
  full-150 run.

## 3. Tasks

- [ ] 112: helper determinista `extract_trick_from_text(text, catalog_names)`
  + wiring en `_build_state` con precedencia vídeo > texto > `None` +
  tests `test_trick_extraction*.py`.
- [ ] 113: incluir dominio `catalog` en `QUERY_DOMAINS` para la ruta de
  progresión + prompt P4 con ejemplo handspring→6 transiciones + tests de
  ruteo.
- [ ] 114: shaping "what next" (lista de candidatos desde forward
  transitions + disclaimer cuando la confianza es baja) + UC bank #27 verde.

## 4. Endpoints

Sin endpoints nuevos. Superficie afectada (contrato interno):

| Seam | Entrada | Salida |
| :--- | :--- | :--- |
| `_build_state` (`coach_providers.py:742-774`) | turno usuario (texto libre + vídeo opcional) | `state.trick_name` resuelto o `None` genuino |
| `resolve_trick` (`gating.py:101-110`) | `trick_name` | `unknown` solo cuando ningún canal aporta truco |
| query graph (`graphs/query.py:48`) | pregunta de progresión | ruta catalog-first (113) |

## 5. Dependencies & Acceptance

- **Blocks:** — (112 desbloquea 113/114; ver tickets).
- **Blocked By:** — (catálogo con 447 movimientos ya disponible; 110
  catalog stores como contexto, no prerrequisito de código).

Acceptance (resumen; detalle por ticket):

- **UC-01 (112):** *"I am able to do the handspring. Which other trick can I
  try now?"* sin vídeo → `trick_name=handspring` (determinista, sin LLM).
- **UC-02 (113):** pregunta de progresión con `handspring` rutea a
  catalog-first; candidatos = las 6 forward transitions del catálogo.
- **UC-03 (114 / bank #27):** *"Analyse my latest handspring video and tell
  me what to focus on first"* con vídeo → label del vídeo manda; respuesta
  "what next" con focos ordenados.
- `pixi run test-api` verde, cobertura ≥ 80%.
