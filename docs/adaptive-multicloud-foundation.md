# Adaptive Multi-Cloud Landing Zone Orchestrator — foundation

This phase preserves the existing Project Designer, scoring, controls, simulation,
Terraform, validation and CI/CD lab. It adds a provider-neutral foundation only;
there are no cloud SDKs, credentials, live connections, publication or apply.

## Module boundaries

- `models`: common Cloud Resource Model and granular control records.
- `adapters`: replaceable AWS, Azure and GCP demo adapters.
- `history`: immutable local scenario snapshots and comparisons.
- `governance`: fail-closed operational-level authorization and redaction.
- `plugins`: semantic-versioned, audited, allowlisted manifests.
- `orchestrator`: coordinates adapters only after governance authorization.
- existing `platform_lab`: scoring, simulation, Terraform, validation and CI/CD.

The UI and orchestrator depend on the common model. Provider-specific translation
stays inside adapters. Plugins cannot request credentials, apply or publication.

## Migration plan

1. Foundation (this release): common model, demo adapters, local history,
   governance/orchestrator/plugin skeletons and four-part navigation.
2. Import boundary: validated JSON/YAML and Terraform-state summaries, still local.
3. Read-only connectors: explicit per-provider adapters behind governance.
4. Advanced scenarios: IAM, network, incidents, regional failure, cost and load.
5. Controlled delivery: external test/plan integrations with approvals; apply remains
   a separately authorized future capability.

Historical evidence is immutable. Recommendations create new snapshots and never
rewrite previous observations.
