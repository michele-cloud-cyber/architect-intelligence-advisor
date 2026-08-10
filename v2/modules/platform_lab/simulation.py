"""Deterministic before/after simulation with per-control attribution."""

from __future__ import annotations

from v2.modules.platform_lab.models import SimulationResult
from v2.modules.platform_lab.scoring import evaluate_controls, overall_score


def simulate_s3_changes(configuration: dict[str, bool | str], changes: tuple[str, ...]) -> SimulationResult:
    before_results, before_scores = evaluate_controls(configuration)
    proposed = dict(configuration)
    for key in changes:
        proposed[key] = True
    after_results, after_scores = evaluate_controls(proposed)
    before_overall = overall_score(before_scores)
    after_overall = overall_score(after_scores)
    before_by_id = {item.definition.control_id: item for item in before_results}
    contributions = []
    for after in after_results:
        before = before_by_id[after.definition.control_id]
        if after.score != before.score:
            contributions.append({
                "control": after.definition.control_id,
                "category": after.definition.category,
                "weight": after.definition.weight,
                "before": before.score,
                "after": after.score,
                "reason": after.rationale,
            })
    eliminated = tuple(item.definition.description for item in before_results if item.score == 0 and proposed.get(item.definition.input_key) is True)
    residual = tuple(item.definition.description for item in after_results if item.score == 0)
    absolute = after_overall - before_overall
    percentage = round((absolute / before_overall * 100), 1) if before_overall else (100.0 if absolute else 0.0)
    return SimulationResult(
        before_scores, after_scores, before_overall, after_overall, absolute, percentage,
        eliminated, residual, (),
        ("Create the protected log bucket before enabling access logging.", "Apply lifecycle policy after versioning to manage retained versions."),
        "Configuration-only change. Existing objects may require separate encryption or migration treatment.",
        "$1–15/month in the demo estimate, driven by logs, monitoring, storage and request volume.",
        100, tuple(contributions), proposed,
    )
