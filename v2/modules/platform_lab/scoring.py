"""Transparent deterministic scoring rules for the phase-one S3 slice."""

from __future__ import annotations

from collections import defaultdict

from v2.modules.platform_lab.models import (
    ControlDefinition, ControlResult, OperatingMode, ProjectAnalysis,
    ProjectDefinition, ResultStatus,
)


CATEGORIES = (
    "Security", "IAM & Access Control", "Network", "Audit & Compliance",
    "Data Protection", "Reliability", "Operational Excellence", "Cost Optimization",
)


def controls_for(language: str = "en") -> tuple[ControlDefinition, ...]:
    it = language == "it"
    def text(en: str, italian: str) -> str:
        return italian if it else en
    return (
        ControlDefinition("S3-PUB-001", "Security", text("Block all public S3 access", "Blocca completamente l'accesso pubblico S3"), "block_public_access", 25, text("Enable all S3 public access block flags.", "Abilita tutti i flag S3 Public Access Block."), "aws_s3_bucket_public_access_block", "test_public_access_block", "$0", 4, 5, 90),
        ControlDefinition("S3-TLS-001", "Network", text("Require TLS for every S3 request", "Richiedi TLS per ogni richiesta S3"), "enforce_tls", 15, text("Add an explicit deny for insecure transport.", "Aggiungi un deny esplicito per il trasporto non sicuro."), "aws_s3_bucket_policy.aws:SecureTransport", "test_tls_policy", "$0", 3, 4, 88),
        ControlDefinition("S3-IAM-001", "IAM & Access Control", text("Use scoped bucket permissions", "Usa permessi limitati sul bucket"), "least_privilege", 20, text("Grant only required S3 actions and resources.", "Concedi soltanto azioni e risorse S3 necessarie."), "aws_iam_policy / aws_s3_bucket_policy", "test_no_unjustified_wildcard", "$0", 3, 5, 82),
        ControlDefinition("S3-ENC-001", "Data Protection", text("Encrypt objects at rest", "Cifra gli oggetti a riposo"), "encryption", 25, text("Configure default S3 server-side encryption.", "Configura la cifratura server-side predefinita di S3."), "aws_s3_bucket_server_side_encryption_configuration", "test_default_encryption", "$0", 3, 5, 90),
        ControlDefinition("S3-VER-001", "Reliability", text("Enable bucket versioning", "Abilita il versioning del bucket"), "versioning", 20, text("Enable S3 versioning for recovery.", "Abilita il versioning S3 per il ripristino."), "aws_s3_bucket_versioning", "test_versioning_enabled", "$0", 3, 4, 86),
        ControlDefinition("S3-LOG-001", "Audit & Compliance", text("Enable server access logging", "Abilita il logging degli accessi server"), "logging", 20, text("Send access logs to a dedicated protected bucket.", "Invia i log di accesso a un bucket dedicato e protetto."), "aws_s3_bucket_logging", "test_access_logging", "$1–5", 3, 4, 84),
        ControlDefinition("S3-MON-001", "Operational Excellence", text("Enable observable access events", "Abilita eventi di accesso osservabili"), "monitoring", 10, text("Monitor access and configuration changes.", "Monitora accessi e modifiche di configurazione."), "aws_cloudwatch_metric_alarm / CloudTrail data events", "test_monitoring_declared", "$1–10", 2, 3, 80),
        ControlDefinition("S3-LCY-001", "Cost Optimization", text("Define lifecycle management", "Definisci la gestione del ciclo di vita"), "lifecycle", 10, text("Expire or transition old versions and logs.", "Scadi o trasferisci versioni e log obsoleti."), "aws_s3_bucket_lifecycle_configuration", "test_lifecycle_rule", text("Usage dependent", "Dipende dall'utilizzo"), 2, 2, 85),
    )


S3_CONTROLS = controls_for("en")


def evaluate_controls(configuration: dict[str, bool | str], language: str = "en") -> tuple[list[ControlResult], dict[str, int | None]]:
    results: list[ControlResult] = []
    grouped: dict[str, list[tuple[int, int]]] = defaultdict(list)
    it = language == "it"
    for control in controls_for(language):
        raw = configuration.get(control.input_key)
        if raw is None or raw == "unknown":
            result = ControlResult(control, "Sconosciuta" if it else "Unknown", 0, ResultStatus.INSUFFICIENT, "Sconosciuta" if it else "Unknown", "Nessuna evidenza disponibile; controllo escluso dal punteggio." if it else "No evidence was provided; this control is excluded from the score.", 0)
        elif bool(raw):
            rationale = (f"{control.control_id} soddisfatto. Il punteggio resta {control.residual_score}/100 per rischio residuo e assenza di verifica AWS." if it else f"{control.control_id} is satisfied. Score remains {control.residual_score}/100 due to residual risk and no AWS verification.")
            result = ControlResult(control, "Abilitata" if it else "Enabled", control.residual_score, ResultStatus.CORRECT, "Bassa" if it else "Low", rationale, 55)
            grouped[control.category].append((control.residual_score, control.weight))
        else:
            severity = "Critica" if it and control.weight >= 25 else "Alta" if it and control.weight >= 20 else "Media" if it else "Critical" if control.weight >= 25 else "High" if control.weight >= 20 else "Medium"
            status = ResultStatus.HIGH_RISK if control.weight >= 20 else ResultStatus.MEDIUM_RISK
            rationale = (f"{control.control_id} non soddisfatto; peso dichiarato {control.weight}." if it else f"{control.control_id} is not satisfied; declared weight is {control.weight}.")
            result = ControlResult(control, "Disabilitata" if it else "Disabled", 15, status, severity, rationale, 55)
            grouped[control.category].append((15, control.weight))
        results.append(result)
    scores = {category: _weighted(grouped.get(category, [])) for category in CATEGORIES}
    return results, scores


def _weighted(values: list[tuple[int, int]]) -> int | None:
    return round(sum(score * weight for score, weight in values) / sum(weight for _, weight in values)) if values else None


def overall_score(scores: dict[str, int | None]) -> int:
    evaluated = [value for value in scores.values() if value is not None]
    return round(sum(evaluated) / len(evaluated)) if evaluated else 0


def maturity_score(configuration: dict[str, bool | str]) -> int:
    enabled = sum(value is True for value in configuration.values())
    coverage = enabled / max(len(configuration), 1)
    return round(20 + coverage * 58)  # capped at 78 without operational evidence


def input_quality(project: ProjectDefinition) -> int:
    fields = (project.objective, project.description, project.identities, project.network_requirements,
              project.security_requirements, project.compliance, project.availability, project.backup_dr,
              project.budget, project.constraints)
    completeness = sum(bool(value.strip()) for value in fields) / len(fields)
    provenance_cap = 45 if project.mode == OperatingMode.DEMO else 65
    return min(round(completeness * 70), provenance_cap)


def analyze_project(project: ProjectDefinition, language: str = "en") -> ProjectAnalysis:
    it = language == "it"
    labels = (("obiettivo", "objective", project.objective), ("requisiti di sicurezza", "security requirements", project.security_requirements), ("backup e disaster recovery", "backup and disaster recovery", project.backup_dr), ("budget", "budget", project.budget))
    missing = tuple((italian if it else english) for italian, english, value in labels if not value.strip())
    contradictions = ()
    if project.data_classification.lower() in {"confidential", "restricted", "riservati", "confidenziali"} and not project.configuration.get("encryption"):
        contradictions = (("Sono dichiarati dati sensibili ma la cifratura predefinita è disabilitata." if it else "Sensitive data is declared while default encryption is disabled."),)
    results, _ = evaluate_controls(project.configuration, language)
    risks = tuple(item.definition.description for item in results if item.score == 15)
    dependencies = (("Il logging richiede un bucket di destinazione separato e protetto.", "Il versioning va associato a regole lifecycle per controllare i costi.") if it else ("Access logging requires a separate protected destination.", "Versioning should be paired with lifecycle rules to control cost."))
    improvements = tuple(item.definition.remediation for item in results if item.score == 15)
    return ProjectAnalysis(missing, contradictions, risks, dependencies, improvements)
