# CI Security for Small Teams

**Section:** AI Applications

## What it delivers
A reasonable security posture without a dedicated security engineer — so your
pipeline catches vulnerable images and bad deploys before they reach users.

## How it's built
Trivy image-vulnerability scanning, environment protection (dev auto, staging
manual, prod gated), and deployment notifications to Slack.

## Proof
- **Code:** [.github/workflows](https://github.com/fpalero/pole-ai-ml/tree/develop/.github/workflows)
- **Live in the pole app:** every deploy is gated by the scan stage
