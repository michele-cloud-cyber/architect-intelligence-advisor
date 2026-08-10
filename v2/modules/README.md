# Architect Advisor V2 extension modules

Each directory in this package is an independent V2 module. Modules expose an
application-facing service through their own package and depend on shared contracts
rather than dashboard internals.

| Module | Responsibility | Status |
| --- | --- | --- |
| `ai_storytelling` | Evidence-based executive and technical narratives | Available |
| `forecast_engine` | Risk and posture forecasting | Available |
| `landing_zone_timeline` | Chronological infrastructure and assessment events | Available |
| `fingerprint_engine` | Versioned architectural fingerprinting | Available |
| `security_findings` | Correlated security dossier and explainable risk | Demo MVP |
| `platform_lab` | Project design, scoring, simulation and secure S3 Terraform slice | Phase 1 available |
| `finops_dashboard` | Cost, efficiency and FinOps metrics | Planned |
| `recommendation_engine` | Prioritized remediation backlog | Planned |
| `what_if_simulator` | Safe remediation impact simulation | Planned |
