# Ticket: PAIML-POLE-ANALYST-079

## Title
[Test-hygiene] Repair red baseline (9 files/80 tests) + add `lint` target + FE PR checks before `/oc` review

## Description
Fase 31 — ver [PLAN_PHASE_31](../plan/PLAN_PHASE_31.md). Hallazgo del pre-PR
QA de `PAIML-POLE-ANALYST-078` (2026-09-10, verificado en `develop`):

- `npx ng test --watch=false` rojo pre-existente: **9 ficheros / 80 tests**
  (errores de provider `KEYCLOAK` en specs `api-client`, `videos-library`,
  `library-page`; `app.spec` con nav-count 2 vs 3 items en código;
  `analysis-tab`/`tips-panel`/`detail-page`).
- `angular.json` (`pole_analyst`) solo expone `build/serve/test` — no hay `lint`.
- `.github/workflows/` (`opencode.yml`, `build-push.yml`,
  `build-reconcile.yml`, `cleanup-worktrees.yml`) no tiene ningún check de PR
  que corra lint/test/build del FE. `opencode.yml` ya prohíbe mergear con
  checks en rojo ("Never merge if CI checks are failing"), así que un check
  requerido de lint queda automáticamente **antes** del review/merge `/oc`.

El ticket 078 cubre solo tests afectados por el responsive. Este ticket deja
el baseline verde y añade el gate de lint.

## What to Do (Implementation Steps)
- [ ] Reparar baseline: re-ejecutar `npx ng test --watch=false` en worktree
  desde `develop` y arreglar los 9 ficheros/80 tests (providers KEYCLOAK en
  specs, nav-count en `app.spec`, `analysis-tab`/`tips-panel`/`detail-page`).
  Solo specs/harness — sin cambiar comportamiento de componentes.
- [ ] Añadir `lint`: `ng add @angular-eslint/schematics` (o equivalente
  manual si el schematic no aplica a Angular 22) + target `lint` en
  `angular.json`; dejar `npx ng lint` limpio (cero warnings o baseline
  justificado en el PR).
- [ ] CI de PR: nuevo workflow (p.ej. `.github/workflows/fe-checks.yml`)
  con `on: pull_request` + `paths: app/pole_analyst/**`, jobs `ng lint` +
  `ng test --watch=false` + `ng build` (Node desde `.nvmrc`/`package.json`
  engines si existe; `npm ci` con caché). **Runners: `runs-on: self-hosted`**
  (convención del repo — `build-push.yml` usa `[self-hosted, Linux, X64]`,
  `opencode/reconcile/cleanup` usan `self-hosted`; prohibido `ubuntu-latest`,
  billing bypass PAIML-INFRA-029).
- [ ] Verificar orden: en el PR de este ticket el check FE debe aparecer en
  verde; (opcional) push temporal con un error de lint para probar que el
  check falla y `/oc` no mergea; revertir la prueba.
- [ ] Documentar en el PR que el usuario debe marcar el check como requerido
  (Settings → Branches → `develop`); los agentes no tocan settings.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `npx ng test --watch=false` verde (0 fallos) en `develop` + worktree.
- [ ] `npx ng lint` existe y pasa limpio.
- [ ] El PR muestra el check FE en verde; con lint roto el check falla.
- [ ] `npx ng build` OK.
- [ ] Zero backend change. Zero cambios visuales.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`
- [ ] `npx ng lint`
- [ ] `npx ng build`
- [ ] `gh pr checks <num>` en verde (incl. el nuevo check FE)

## Dependencies
- **Blocks**: None.
- **Blocked By**: None (validator-clean batch).
- **Sequencing note (no formal gate):** ambos tickets tocan specs de
  `app/pole_analyst` — arrancar 079 cuando el PR de 078 esté **merged** en
  `develop` para evitar colisiones de merge (verificar con
  `gh pr view --json state,merged` + `gh pr checks`).

## Estimated Effort
- [M]
