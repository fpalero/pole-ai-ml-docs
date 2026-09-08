# Ticket: PAIML-INFRA-028

## Title
[Infra] Raise Traefik WebSocket timeouts on pole-analyst + pole-fe ingresses (fix chatbot answers never reaching the browser)

## Description
**ROOT CAUSE:** The analyst chatbot (and the generic chatbot) is a WebSocket
conversation where a single agent turn can run 1–3 minutes (the LLM agent
loop + tool calls, e.g. RAG embedding loads, segment insight fetches). The
browser ↔ `pole_api` connection is proxied by two hops: the inner nginx in
the FE pod (which already sets `proxy_read_timeout 300s`) and the **outer
Traefik ingress** that fronts both FE apps.

Traefik's default WebSocket/response timeouts are ~60s, far shorter than a
long agent turn. When a turn exceeds that, Traefik resets the upgraded
connection mid-turn — the backend still finishes the `agent_reply`, but the
socket is already dead, so **the browser never receives an answer** and the
FE `Thinking` chip eventually times out to `Error` (180s client timeout).

**Observed 2026-09-08 (ipsf-server / staging):**
- `pole_api` log: `analyst chat turn ... duration=147.61s status=ACTIVE` — the
  agent DID produce a reply.
- Traefik ingress log at 13:12:58 (44s into that same turn):
  `recv() failed (104: Connection reset by peer) while proxying upgraded
  connection ... /api/analyst-chatbot/ws/analyst-chat`.
- `pole-analyst` nginx log: the client reconnected repeatedly
  (13:10:36, 13:12:58, 13:15:01, 13:16:31) yet never received an
  `agent_reply` → "no answer" from the user's perspective.

## Affected Components
- `infrastracture/helm/pole-ai/charts/pole-analyst/templates/ingress.yaml`
  (host `pole-coach.duckdns.org` — the app the user reported)
- `infrastracture/helm/pole-ai/charts/pole-fe/templates/ingress.yaml`
  (host `pole-ml.duckdns.org` — same WS chatbot flows)

## What to Do (Implementation Steps)
- [x] Step 1: Add Traefik WebSocket timeout annotations to the
      `pole-analyst` Ingress:
      - `traefik.ingress.kubernetes.io/proxy-read-timeout: "600"`
      - `traefik.ingress.kubernetes.io/proxy-write-timeout: "600"`
      - `traefik.ingress.kubernetes.io/proxy-idle-timeout: "600"`
- [x] Step 2: Apply the same three annotations to the `pole-fe` Ingress.
- [ ] Step 3: Redeploy the umbrella chart to ipsf-server (staging) and
      verify the annotations are live on the Ingress objects.
- [ ] Step 4: E2E — open the analyst chat, send a message that forces a
      long turn, and confirm the `agent_reply` reaches the browser
      (no `Connection reset` in Traefik logs; FE `Thinking → Completed`
      resolves with the answer).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `pole-analyst` and `pole-fe` Ingresses carry the three 600s Traefik
      timeout annotations in the chart.
- [ ] `helm template` / `helm lint` clean; annotations present on the
      rendered Ingress manifests.
- [ ] Redeployed to staging; `kubectl get ingress -n pole-ai -o yaml`
      shows the annotations.
- [ ] E2E evidence: a long analyst-chatbot turn completes and the answer is
      displayed in the FE with no mid-turn disconnect (Traefik log shows no
      `recv() failed` / `Connection reset` for the WS path).

## Integration Tests to Run (Local / Staging Verification)
- [ ] `helm lint` on `pole-analyst` + `pole-fe`.
- [ ] `helm template pole-ai helm/pole-ai --show-only .../ingress.yaml`
      shows the annotations on both ingresses.
- [ ] Staging E2E: long chatbot turn lands its `agent_reply`; confirm no
      WS reset in the Traefik/nginx logs.

## Dependencies
- **Blocks:** —
- **Blocked By:** —

## Estimated Effort
- [XS] (Very Small — ~15 min + redeploy)
