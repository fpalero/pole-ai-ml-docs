# Ticket: PAIML-INFRA-012

## Title
[Infrastructure] Add Slack Notification Job to Deploy Workflows

## Description
Add a notification job to deploy workflows (deploy-dev, deploy-staging, deploy-prod) that posts to Slack on success or failure. Uses `slackapi/slack-github-action@v1`.

## What to Do (Implementation Steps)
- [ ] Step 1: Add `notify` job to `.github/workflows/deploy-dev.yml`
- [ ] Step 2: Add `notify` job to `.github/workflows/deploy-staging.yml`
- [ ] Step 3: Add `notify` job to `.github/workflows/deploy-prod.yml`
- [ ] Step 4: Configure each notify job with `if: always()` to run even on failure
- [ ] Step 5: Use `slackapi/slack-github-action@v1` with webhook payload
- [ ] Step 6: Include in payload: deploy status, commit SHA, environment name, workflow run URL
- [ ] Step 7: Format: `{"text": "Deploy <status>: <sha> to <env> — <workflow_url>"}`

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] All three deploy workflows have a `notify` job
- [ ] Notification sends on both success and failure
- [ ] Payload includes: status, SHA, environment, workflow URL
- [ ] Notification uses `SLACK_WEBHOOK_URL` secret

## Integration Tests to Run (Local Verification)
- [ ] Run UC-05: Slack notification on deploy outcome — trigger a deploy, verify Slack message is received

## Dependencies
- **Blocks:** None
- **Blocked By:** PAIML-INFRA-011 (webhook secret must exist), PAIML-INFRA-005/008/010 (deploy workflows must exist)

## Estimated Effort
- [S] (Small < 1h)
