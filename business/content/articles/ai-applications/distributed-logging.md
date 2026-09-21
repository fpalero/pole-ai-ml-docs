# Distributed Logging on a Budget

**Section:** AI Applications

## What it delivers
Centralized logs for an ML stack without a Splunk-sized bill — observability
that fits on one node.

## How it's built
Single-node Elasticsearch via Helm on k3s, Filebeat shipping app and package
logs, index-lifecycle management, and green/yellow health as the acceptance
gate.

## Proof
- **Code:** [infrastracture/helm](https://github.com/fpalero/pole-ai-ml-infra/tree/develop/helm)
- **Live in the pole app:** cluster-wide log shipping on staging
