"""Deterministic before/after simulation with residual risk and attribution."""

from __future__ import annotations

from v2.modules.platform_lab.models import OperatingMode, ProjectDefinition, SimulationResult
from v2.modules.platform_lab.scoring import evaluate_controls, input_quality, maturity_score, overall_score


def simulate_s3_changes(configuration: dict[str, bool | str], changes: tuple[str, ...], project: ProjectDefinition | None = None, language: str = "en") -> SimulationResult:
    before_results, before_scores = evaluate_controls(configuration, language)
    proposed = dict(configuration)
    for key in changes:
        proposed[key] = True
    after_results, after_scores = evaluate_controls(proposed, language)
    before_technical, after_technical = overall_score(before_scores), overall_score(after_scores)
    before_maturity, after_maturity = maturity_score(configuration), maturity_score(proposed)
    quality = input_quality(project) if project else (45 if language == "it" else 45)
    before_by_id = {item.definition.control_id: item for item in before_results}
    contributions = tuple({"control": item.definition.control_id, "category": item.definition.category, "weight": item.definition.weight, "before": before_by_id[item.definition.control_id].score, "after": item.score, "absolute_points": item.score - before_by_id[item.definition.control_id].score, "reason": item.rationale} for item in after_results if item.score != before_by_id[item.definition.control_id].score)
    eliminated = tuple(item.definition.description for item in before_results if item.score == 15 and proposed.get(item.definition.input_key) is True)
    residual = tuple((f"Rischio residuo: {item.definition.description}" if language == "it" else f"Residual risk: {item.definition.description}") for item in after_results if item.score < 100)
    absolute = after_technical - before_technical
    percentage = round(absolute / before_technical * 100, 1) if before_technical else 0.0
    confidence = min(quality + 10, 55 if (project is None or project.mode == OperatingMode.DEMO) else 70)
    dependencies = (("Creare il bucket log prima di abilitare il logging.", "Associare lifecycle e versioning.") if language == "it" else ("Create the log bucket before enabling logging.", "Pair lifecycle management with versioning."))
    impact = "Modifica solo di configurazione; gli oggetti esistenti possono richiedere migrazione separata." if language == "it" else "Configuration-only change; existing objects may require separate migration."
    cost = "Stima demo $1–15/mese; dipende da log, richieste e storage." if language == "it" else "Demo estimate $1–15/month; depends on logs, requests and storage."
    return SimulationResult(before_scores, after_scores, before_technical, after_technical, absolute, percentage, eliminated, residual, (), dependencies, impact, cost, confidence, contributions, proposed, before_technical, after_technical, before_maturity, after_maturity, quality)
