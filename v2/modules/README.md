# Architect Advisor V2 extension modules

Each directory in this package is a reserved, independent V2 module. A future module should expose an application-facing service through its own package and depend on shared contracts rather than dashboard internals.

Planned modules do not contain functional implementations yet.

| Module | Intended responsibility |
| --- | --- |
| `ai_storytelling` | Evidence-based executive and technical narratives |
| `forecast_engine` | Risk and posture forecasting |
| `landing_zone_timeline` | Chronological infrastructure and assessment events |
| `fingerprint_engine` | Versioned architectural fingerprinting |
| `finops_dashboard` | Cost, efficiency and FinOps metrics |
| `recommendation_engine` | Prioritized remediation backlog |
| `what_if_simulator` | Safe remediation impact simulation |
