"""Safe Terraform package generator for the S3 vertical slice."""

from __future__ import annotations

from difflib import unified_diff
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

from v2.modules.platform_lab.models import ProjectDefinition, SimulationResult, TerraformPackage


def generate_s3_package(project: ProjectDefinition, simulation: SimulationResult, language: str = "en") -> TerraformPackage:
    files = {
        "versions.tf": '''terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}
''',
        "providers.tf": '''provider "aws" {
  region = var.aws_region
  default_tags { tags = local.common_tags }
}
''',
        "variables.tf": '''variable "aws_region" { type = string }
variable "environment" { type = string }
variable "project_name" { type = string }
variable "bucket_name" { type = string }
variable "log_bucket_name" { type = string }
''',
        "locals.tf": '''locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
''',
        "main.tf": _main_tf(),
        "outputs.tf": '''output "bucket_arn" { value = aws_s3_bucket.workload.arn }
output "log_bucket_arn" { value = aws_s3_bucket.access_logs.arn }
''',
        "README.md": _readme(project),
        "examples/dev.tfvars": '''aws_region     = "eu-west-1"
environment    = "development"
project_name   = "replace-me"
bucket_name    = "replace-with-globally-unique-name"
log_bucket_name = "replace-with-unique-log-bucket-name"
''',
        "tests/s3_security.tftest.hcl": _test_hcl(),
    }
    mappings = (
        {"control": "S3-PUB-001", "terraform": "aws_s3_bucket_public_access_block.workload", "test": "test_public_access_block"},
        {"control": "S3-ENC-001", "terraform": "aws_s3_bucket_server_side_encryption_configuration.workload", "test": "test_default_encryption"},
        {"control": "S3-VER-001", "terraform": "aws_s3_bucket_versioning.workload", "test": "test_versioning_enabled"},
        {"control": "S3-LOG-001", "terraform": "aws_s3_bucket_logging.workload", "test": "test_access_logging"},
        {"control": "S3-TLS-001", "terraform": "aws_s3_bucket_policy.require_tls", "test": "test_tls_policy"},
        {"control": "S3-LCY-001", "terraform": "aws_s3_bucket_lifecycle_configuration.workload", "test": "test_lifecycle_rule"},
    )
    it = language == "it"
    explanations = (
        {"resource": "aws_s3_bucket.workload", "explanation": "Bucket applicativo senza eliminazione forzata." if it else "Workload bucket with force deletion disabled."},
        {"resource": "aws_s3_bucket_public_access_block.workload", "explanation": "Blocca ACL e policy pubbliche." if it else "Blocks public ACLs and bucket policies."},
        {"resource": "aws_s3_bucket_server_side_encryption_configuration.workload", "explanation": "Applica cifratura AES256 predefinita." if it else "Applies default AES256 encryption."},
        {"resource": "aws_s3_bucket_versioning.workload", "explanation": "Conserva versioni per il recupero." if it else "Retains versions for recovery."},
        {"resource": "aws_s3_bucket_logging.workload", "explanation": "Invia access log a un bucket separato." if it else "Sends access logs to a separate bucket."},
        {"resource": "aws_s3_bucket_policy.require_tls", "explanation": "Nega richieste senza TLS." if it else "Denies requests without TLS."},
    )
    previous = _baseline_tf(project.configuration)
    diff = "".join(unified_diff(previous.splitlines(True), files["main.tf"].splitlines(True), fromfile="current/main.tf", tofile="proposed/main.tf"))
    return TerraformPackage(files, {
        "decision": "Private, encrypted, versioned S3 bucket with logging and total public access block",
        "resources": ["workload bucket", "access-log bucket", "bucket policy", "lifecycle rule"],
        "account": "Variable / not embedded", "region": project.regions[0] if project.regions else "Variable",
        "environment": project.environments[0] if project.environments else "Variable",
        "dependencies": list(simulation.dependencies), "score_before": simulation.before_overall,
        "score_after": simulation.after_overall, "risks": list(simulation.residual_risks),
        "estimated_cost": simulation.estimated_cost, "side_effects": simulation.operational_impact,
        "confidence": simulation.confidence,
    }, diff, mappings, explanations)


def package_zip_bytes(package: TerraformPackage) -> bytes:
    """Return an in-memory ZIP; no credentials or environment values are added."""
    buffer = BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED) as archive:
        for name, content in package.files.items():
            archive.writestr(name, content)
    return buffer.getvalue()


def _baseline_tf(configuration: dict[str, bool | str]) -> str:
    enabled = [key for key, value in configuration.items() if value is True]
    lines = ["# Current simulated configuration (not imported from AWS)\n", 'resource "aws_s3_bucket" "workload" {\n', "  bucket = var.bucket_name\n", "}\n"]
    lines.extend(f"# enabled: {key}\n" for key in sorted(enabled))
    return "".join(lines)


def _main_tf() -> str:
    return '''resource "aws_s3_bucket" "workload" {
  bucket        = var.bucket_name
  force_destroy = false
}

resource "aws_s3_bucket_public_access_block" "workload" {
  bucket                  = aws_s3_bucket.workload.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "workload" {
  bucket = aws_s3_bucket.workload.id
  rule { apply_server_side_encryption_by_default { sse_algorithm = "AES256" } }
}

resource "aws_s3_bucket_versioning" "workload" {
  bucket = aws_s3_bucket.workload.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket" "access_logs" {
  bucket        = var.log_bucket_name
  force_destroy = false
}

resource "aws_s3_bucket_public_access_block" "access_logs" {
  bucket                  = aws_s3_bucket.access_logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_logging" "workload" {
  bucket        = aws_s3_bucket.workload.id
  target_bucket = aws_s3_bucket.access_logs.id
  target_prefix = "access/"
}

resource "aws_s3_bucket_policy" "require_tls" {
  bucket = aws_s3_bucket.workload.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid = "DenyInsecureTransport", Effect = "Deny", Principal = "*", Action = "s3:*"
      Resource = [aws_s3_bucket.workload.arn, "${aws_s3_bucket.workload.arn}/*"]
      Condition = { Bool = { "aws:SecureTransport" = "false" } }
    }]
  })
}

resource "aws_s3_bucket_lifecycle_configuration" "workload" {
  bucket = aws_s3_bucket.workload.id
  rule {
    id = "noncurrent-version-retention"
    status = "Enabled"
    filter {}
    noncurrent_version_expiration { noncurrent_days = 90 }
  }
}
'''


def _readme(project: ProjectDefinition) -> str:
    return f'''# Secure S3 module example

Generated for `{project.name}` in **{project.mode.value}** mode. Review and run
`terraform plan` manually with an approved role. This package never runs apply and
contains no credentials, account IDs, backend, or sensitive values.
'''


def _test_hcl() -> str:
    return '''run "secure_s3_configuration" {
  command = plan
  assert {
    condition = aws_s3_bucket_public_access_block.workload.restrict_public_buckets
    error_message = "Public bucket access must be fully blocked."
  }
  assert {
    condition = aws_s3_bucket_versioning.workload.versioning_configuration[0].status == "Enabled"
    error_message = "Versioning must be enabled."
  }
}
'''
