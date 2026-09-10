# Fase 31 — Baseline test repair + lint gate (pole_analyst) — ✅ DONE (code PR #300)

> Plan maestro: [PLAN.md](../PLAN.md) · Backend requerido: ninguno (FE-only +
> repo CI). Origen: hallazgo del pre-PR QA de `PAIML-POLE-ANALYST-078`
> (2026-09-10): el baseline de `develop` está rojo y no existe target `lint`.

## Contexto

Verificado en `develop` (2026-09-10):
- `npx ng test --watch=false` rojo pre-existente: 9 ficheros / 80 tests
  (errores de provider `KEYCLOAK` en specs `api-client`/`videos-library`/
  `library-page`, `app.spec` con nav-count 2 vs 3 items en código,
  `analysis-tab`/`tips-panel`/`detail-page`).
- `angular.json` (`pole_analyst`) solo tiene targets `build/serve/test` —
  **no hay `lint`**.
- `.github/workflows/` tiene `opencode.yml` (review vía `/oc`, mergea solo si
  el CI está verde: "Never merge if CI checks are failing"), `build-push.yml`,
  `build-reconcile.yml`, `cleanup-worktrees.yml` — **ningún check de PR que
  corra lint/test/build del FE**.

El ticket 078 cubre solo los tests afectados por el responsive. Este fase deja
el baseline verde y convierte lint+test+build en checks requeridos del PR,
de modo que el review `/oc` nunca mergea con lint roto.

## Tickets

| Ticket | Scope | Estado |
| :--- | :--- | :--- |
| `PAIML-POLE-ANALYST-079` | Reparar baseline rojo (9 ficheros/80 tests) + añadir target `lint` (angular-eslint) + workflow de checks FE en PRs + documentar protección de rama | 📋 PLANNED |

## Tasks

1. **Baseline verde** — reparar los 9 ficheros/80 tests que fallan en
   `develop` sin relación con el responsive (providers KEYCLOAK en specs,
   nav-count, analysis-tab/tips-panel/detail-page). Sin cambiar
   comportamiento; solo specs/harness.
2. **Target `lint`** — añadir `angular-eslint` (`ng add @angular-eslint/schematics`
   o equivalente manual) + target `lint` en `angular.json`; `npx ng lint`
   limpio en `app/pole_analyst`.
3. **CI de PR** — nuevo workflow (p.ej. `fe-checks.yml`, `pull_request` sobre
   `paths: app/pole_analyst/**`) que corre `ng lint` + `ng test --watch=false` +
   `ng build`, con **`runs-on: self-hosted`** (convención del repo, prohibido
   `ubuntu-latest`). Al ser check del PR y dado que `opencode.yml` prohíbe mergear
   con checks fallando, el lint queda **automáticamente antes** del review/merge
   `/oc`, como pide el PO.
4. **Protección de rama (paso manual del usuario)** — documentar en el ticket
   que el check debe marcarse como requerido en Settings → Branches → `develop`
   (los agentes no tocan settings).

## Acceptance

- `npx ng test --watch=false` verde en `develop` (0 fallos).
- `npx ng lint` existe y está limpio.
- PR de prueba muestra el check FE en verde; con lint roto a propósito el
  check falla (y por tanto `/oc` no mergea).
- Cero cambios backend. Cero cambios visuales.

## Dependencies

- **Blocks:** None.
- **Blocked By:** None (batch validator-clean; secuenciación por nota: arrancar
  tras el merge de 078 para evitar colisiones en specs de `app/pole_analyst`).
