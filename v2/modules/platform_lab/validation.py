"""Local validation report; it never claims remote AWS execution."""

from __future__ import annotations

import shutil

from v2.modules.platform_lab.models import TerraformPackage, ValidationResult


def validate_s3_package(package: TerraformPackage) -> tuple[ValidationResult, ...]:
    main = package.files.get("main.tf", "")
    results = [
        _local("Policy: no public bucket", "custom:S3-PUB-001", all(flag in main for flag in ("block_public_acls       = true", "block_public_policy     = true", "ignore_public_acls      = true", "restrict_public_buckets = true")), "All public-access-block flags must be true."),
        _local("Policy: encryption required", "custom:S3-ENC-001", "server_side_encryption_configuration" in main and "AES256" in main, "Default encryption is declared."),
        _local("Policy: logging required", "custom:S3-LOG-001", "aws_s3_bucket_logging" in main, "A dedicated access-log destination is declared."),
        _local("Policy: TLS required", "custom:S3-TLS-001", "aws:SecureTransport" in main and 'Effect = "Deny"' in main, "Insecure transport is explicitly denied."),
        _local("Policy: accidental deletion protection", "custom:S3-DEL-001", main.count("force_destroy = false") >= 2, "Both buckets disable force destruction."),
    ]
    for executable, command in (("terraform", "terraform fmt -check / init -backend=false / validate / test"), ("tflint", "tflint"), ("checkov", "checkov -d .")):
        available = shutil.which(executable) is not None
        results.append(ValidationResult(executable, command, "Not executed", "Available locally" if available else "Tool not installed", "Generation does not automatically execute external tools or a real plan."))
    results.append(ValidationResult("Terraform plan", "terraform plan", "Not executed", "No AWS credentials or approved target supplied", "A real plan requires an explicit environment, reviewed role, and manual authorization."))
    return tuple(results)


def _local(name: str, command: str, passed: bool, rationale: str) -> ValidationResult:
    return ValidationResult(name, command, "Passed" if passed else "Failed", "Deterministic local source inspection", rationale)
