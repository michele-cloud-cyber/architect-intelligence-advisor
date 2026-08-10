"""Local validation report; it never claims remote AWS execution."""

from __future__ import annotations

import shutil

from v2.modules.platform_lab.models import TerraformPackage, ValidationResult


def validate_s3_package(package: TerraformPackage, language: str = "en") -> tuple[ValidationResult, ...]:
    main = package.files.get("main.tf", "")
    it = language == "it"
    results = [
        _local("Policy: nessun bucket pubblico" if it else "Policy: no public bucket", "custom:S3-PUB-001", all(flag in main for flag in ("block_public_acls       = true", "block_public_policy     = true", "ignore_public_acls      = true", "restrict_public_buckets = true")), "Tutti i flag di blocco pubblico devono essere true." if it else "All public-access-block flags must be true.", it),
        _local("Policy: cifratura obbligatoria" if it else "Policy: encryption required", "custom:S3-ENC-001", "server_side_encryption_configuration" in main and "AES256" in main, "È dichiarata la cifratura predefinita." if it else "Default encryption is declared.", it),
        _local("Policy: logging obbligatorio" if it else "Policy: logging required", "custom:S3-LOG-001", "aws_s3_bucket_logging" in main, "È dichiarata una destinazione log dedicata." if it else "A dedicated access-log destination is declared.", it),
        _local("Policy: TLS obbligatorio" if it else "Policy: TLS required", "custom:S3-TLS-001", "aws:SecureTransport" in main and 'Effect = "Deny"' in main, "Il trasporto non sicuro è negato esplicitamente." if it else "Insecure transport is explicitly denied.", it),
        _local("Policy: protezione eliminazione accidentale" if it else "Policy: accidental deletion protection", "custom:S3-DEL-001", main.count("force_destroy = false") >= 2, "Entrambi i bucket disabilitano l'eliminazione forzata." if it else "Both buckets disable force destruction.", it),
    ]
    for executable, command in (("terraform", "terraform fmt -check / init -backend=false / validate / test"), ("tflint", "tflint"), ("checkov", "checkov -d .")):
        available = shutil.which(executable) is not None
        result = ("Disponibile localmente" if available else "Strumento non installato") if it else ("Available locally" if available else "Tool not installed")
        rationale = "La generazione non esegue automaticamente strumenti esterni o plan reali." if it else "Generation does not automatically execute external tools or a real plan."
        results.append(ValidationResult(executable, command, "Not executed", result, rationale))
    results.append(ValidationResult("Terraform plan", "terraform plan", "Not executed", "Nessuna credenziale AWS o target approvato" if it else "No AWS credentials or approved target supplied", "Un plan reale richiede ambiente, ruolo revisionato e autorizzazione manuale." if it else "A real plan requires an explicit environment, reviewed role, and manual authorization."))
    return tuple(results)


def _local(name: str, command: str, passed: bool, rationale: str, italian: bool = False) -> ValidationResult:
    result = "Ispezione deterministica locale del codice" if italian else "Deterministic local source inspection"
    return ValidationResult(name, command, "Passed" if passed else "Failed", result, rationale)
