# AWS Interactive Architecture, Security & Terraform Lab

## Existing application analysis

The current application already provides a stable read-only assessment dashboard,
history adapters, forecasting, architectural fingerprints, AI storytelling, and an
isolated Security Findings dossier. These capabilities remain unchanged and are
available as the **Advisor Dashboard** workspace.

The new lab is additive. It uses the existing `DashboardService` boundary pattern
but keeps project design, scoring, simulation, Terraform generation, and future AWS
connectors in separate packages.

## Operating modes

- **Demo**: deterministic fictional S3 project and findings.
- **Simulation**: configuration entered by the user; no AWS calls.
- **AWS Read-only**: reserved interface only. It will eventually use temporary
  credentials or OIDC and must never mutate AWS.

Mode provenance must be visible in every lab screen and stored with every future
decision.

## Screen wireframe

```text
+--------------------------------------------------------------+
| MODE BADGE | Project name | Evidence provenance              |
+----------------------+---------------------------------------+
| Project Designer     | Analysis: missing / risk / dependency |
| free text + form     | score cards + control table           |
+----------------------+---------------------------------------+
| Proposed changes -> deterministic before/after simulation    |
+--------------------------------------------------------------+
| Decision summary -> Terraform files -> validation -> CI/CD   |
+--------------------------------------------------------------+
```

## Data model

- `ProjectDefinition`: requirements, scope, data classification, recovery and cost.
- `ControlDefinition`: granular ID, category, inputs, weight, rationale,
  remediation, Terraform mapping, and associated test.
- `ControlResult`: current value, score, status, severity and confidence.
- `SimulationResult`: before/after score, eliminated/residual/new risks,
  dependencies, cost, impact, confidence and per-control contribution.
- `TerraformPackage`: generated files and decision provenance.
- `ValidationResult`: command/check, status, output and reason.

## Initial scoring rules

Scores are deterministic weighted averages. Each control is either satisfied,
unsatisfied, or lacks evidence. Satisfied controls receive 100; unsatisfied controls
receive 0; insufficient evidence is excluded and displayed in gray. Category score:

```text
sum(control score * control weight) / sum(evaluated control weights)
```

The S3 vertical slice declares weights in code for public access, encryption,
versioning, access logging, TLS enforcement, least privilege, auditability, backup,
operability, and cost controls. Every simulation delta lists the contributing
control IDs; no random percentages are used.

## Decision to Terraform mapping

| Decision | Terraform property/resource | Test |
| --- | --- | --- |
| Block public access | `aws_s3_bucket_public_access_block` | all four flags true |
| Encrypt objects | `aws_s3_bucket_server_side_encryption_configuration` | AES256/KMS rule |
| Enable versioning | `aws_s3_bucket_versioning` | status is Enabled |
| Enable logging | `aws_s3_bucket_logging` and dedicated log bucket | target configured |
| Enforce TLS | `aws_s3_bucket_policy` explicit deny | `aws:SecureTransport=false` denied |

Generated values use variables and environment-specific inputs; credentials and
real account IDs are never emitted.

## Delivery phases

1. Project Designer, granular scoring, interactive tables, deterministic simulation,
   and the complete S3 vertical slice.
2. General Terraform generation, export, local CLI validation, and richer diffing.
3. IAM Access Lab with local policy evaluation.
4. SCP Policy Lab with lockout and wildcard analysis.
5. Security, network, audit, reliability, data protection, and cost modules.
6. Policy as Code and selectable CI/CD generators.
7. Explicitly authorized AWS read-only connectors.

No phase automatically performs `terraform apply`, AWS mutations, SCP/IAM changes,
repository publication, backend creation, or real pipeline creation.
