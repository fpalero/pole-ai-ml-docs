# Fase 12 — User menu + logout (app shell) — ✅ DONE

> Plan maestro: [PLAN.md](PLAN.md) · Feature: logout desde el header de `pole_fe` vía Keycloak
> end-session — `app/pole_fe/src/app/app.ts` (`AppComponent`).

## Contexto

El app shell no ofrecía forma de cerrar sesión. El botón `account_circle` del header no hacía
nada. Se añade un dropdown de usuario con Logout que termina la sesión SSO en Keycloak.

## Alcance

- Dropdown de usuario sobre el botón `account_circle` (`toggleUserMenu` / `closeUserMenu`,
  backdrop para cerrar).
- `logout()` vía `keycloak.logout({ redirectUri: window.location.origin })` (end-session con
  `id_token_hint`, retorno al origin donde `login-required` muestra el login de nuevo).
- Sin endpoints nuevos; sin cambios de backend.

## Decisión de diseño

Llamada end-session obligatoria: limpiar solo los tokens locales no basta — la cookie SSO
compartida re-autenticaría silenciosamente en el siguiente init. Logout por app imposible con
`login-required`; el logout siempre mata la sesión SSO compartida.

## Tickets

- [x] **PAIML-POLE-FE-013** — User dropdown menu + logout via Keycloak end-session
  (PR fpalero/pole-ai-ml#192).

## Criterios de aceptación

- [x] El menú de usuario abre/cierra correctamente; Logout termina la sesión SSO y vuelve al login.
- [x] `tsc --noEmit` limpio, `ng build` OK, verificado en staging.
