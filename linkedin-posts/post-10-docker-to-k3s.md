# Deploying an ML Stack Solo: docker-compose → k3s

From a local docker-compose to a full k3s cluster with Helm — one solo dev.

The path I took to ship an ML stack without a DevOps team:

- docker-compose for local dev
- k3s + Helm charts for the cluster
- Traefik ingress, health probes
- Trivy vulnerability scans in CI
- GitHub Actions deploying per environment

One recipe, fully reproducible, with security baked into the pipeline stage — not bolted on.

This is how AI Sport Agent gets from my laptop to a live cluster.

What's your go-to for solo ML deployments?

**Hashtags:** #MLOps #Kubernetes #AI #DevOps
