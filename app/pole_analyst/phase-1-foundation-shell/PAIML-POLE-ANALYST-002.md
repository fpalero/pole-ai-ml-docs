# Ticket: PAIML-POLE-ANALYST-002

## Title
[Infrastructure] ApiClient + error interceptor + ng serve proxy

## Description
Provide the HTTP foundation for the FE: an `ApiClient` wrapping Angular `HttpClient` (with
multipart upload progress), an interceptor that maps the backend `{detail}` error envelope into
typed errors, and `ng serve` proxy config forwarding `/api` (REST) + `/ws` (WebSocket) to
`pola_api`.

## What to Do (Implementation Steps)
- [ ] Implement `core/api-client` with GET/POST (json + multipart) and upload progress events.
- [ ] Implement error interceptor normalizing `{detail}` into typed `ApiError`.
- [ ] Add `proxy.conf.json` for `/api` and `/ws` (and `/ws` upgrade).
- [ ] Register the interceptor and client providers in the root module.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `ng lint`/`ng build` pass.
- [ ] A `422 {detail}` response surfaces as a typed error to callers.
- [ ] Dev proxy forwards `/api/*` and `/ws/*` to the backend.

## Integration Tests to Run (Local Verification)
- [ ] UC-01/UC-02/UC-03: services can reach `/api/analysis/*` through the client + proxy.

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-005, PAIML-POLE-ANALYST-006, PAIML-POLE-ANALYST-010, PAIML-POLE-ANALYST-011, PAIML-POLE-ANALYST-015, PAIML-POLE-ANALYST-028
- **Blocked By**: PAIML-POLE-ANALYST-001

## Estimated Effort
- [M]
