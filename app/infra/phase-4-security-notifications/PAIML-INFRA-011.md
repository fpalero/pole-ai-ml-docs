# Ticket: PAIML-INFRA-011

## Title
[Infrastructure] Configure Slack Webhook Secrets

## Description
Configure Slack webhook secrets in GitHub for deployment notifications. These secrets are used by the notification job in deploy workflows.

## What to Do (Implementation Steps)
- [ ] Step 1: Create Slack incoming webhook URL (Slack API dashboard)
- [ ] Step 2: Add `SLACK_WEBHOOK_URL` secret to GitHub repository settings
- [ ] Step 3: Add `SLACK_CHANNEL` secret (optional, for channel targeting)
- [ ] Step 4: Document the webhook setup in README

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `SLACK_WEBHOOK_URL` secret exists in GitHub repository settings
- [ ] Webhook URL is valid and testable
- [ ] Setup documented in infrastructure README

## Integration Tests to Run (Local Verification)
- [ ] Test webhook: `curl -X POST -H 'Content-type: application/json' --data '{"text":"Test notification"}' $SLACK_WEBHOOK_URL`

## Dependencies
- **Blocks:** PAIML-INFRA-012 (notification job needs this secret)
- **Blocked By:** None (can configure independently)

## Estimated Effort
- [S] (Small < 1h)
