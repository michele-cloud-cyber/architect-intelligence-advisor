"""Generate Bedrock narratives from real, comparable Landing Zone snapshots."""

from __future__ import annotations

import json
from typing import Any, Iterable

from v2.modules.landing_zone_timeline import build_timeline


def build_storytelling_prompt(snapshots: Iterable[dict[str, Any]]) -> str | None:
    """Build an evidence-constrained Bedrock prompt from the two latest snapshots."""

    ordered = list(snapshots)
    if len(ordered) < 2:
        return None

    previous, current = ordered[-2], ordered[-1]
    events = build_timeline([previous, current])
    evidence = {
        "previous_snapshot": _snapshot_summary(previous),
        "current_snapshot": _snapshot_summary(current),
        "detected_changes": [event.summary for event in events if event.category != "Assessment"],
        "current_recommendations": _recommendations(current),
    }

    return """You are the Architect Advisor AI Storyteller for an AWS Landing Zone.

Write in Italian for a cloud architect audience. Base every statement exclusively on
the supplied assessment evidence. Do not invent AWS resources, causes, security
incidents, cost information, or remediation results. If the evidence cannot establish
why a change happened, state that the cause is not available in the snapshots.

Produce these exact sections:
1. Cosa è cambiato
2. Perché è cambiato
3. Rischi aumentati
4. Rischi diminuiti
5. Azioni consigliate

For every conclusion, refer to the score movement, finding, fingerprint change, or
recommendation that supports it. Prioritize current recommendations and distinguish
observed facts from reasonable inferences.

Assessment evidence (JSON):
""" + json.dumps(evidence, ensure_ascii=False, indent=2, default=str)


def generate_story(snapshots: Iterable[dict[str, Any]]) -> str:
    """Invoke the existing V1 Bedrock adapter with a historical V2 prompt."""

    prompt = build_storytelling_prompt(snapshots)
    if prompt is None:
        raise ValueError("At least two historical snapshots are required for AI Storytelling.")

    # BedrockEngine remains the only implementation of the Bedrock invocation.
    from sr.engines.bedrock_engine import BedrockEngine

    return BedrockEngine().invoke(prompt)


def _snapshot_summary(snapshot: dict[str, Any]) -> dict[str, Any]:
    fingerprint = snapshot.get("fingerprint") if isinstance(snapshot.get("fingerprint"), dict) else {}
    risk_score = snapshot.get("risk_score")
    if isinstance(risk_score, dict):
        risk_score = risk_score.get("score")
    return {
        "timestamp": snapshot.get("timestamp"),
        "overall_score": snapshot.get("overall_score", fingerprint.get("overall")),
        "risk_score": risk_score,
        "architecture": snapshot.get("architecture", fingerprint.get("architecture")),
        "fingerprint_hash": fingerprint.get("hash"),
        "accounts": _strings(snapshot.get("accounts")),
        "regions": _strings(snapshot.get("regions")),
        "findings": _strings(snapshot.get("findings")),
    }


def _recommendations(snapshot: dict[str, Any]) -> list[dict[str, str]]:
    values = snapshot.get("recommendations")
    if not isinstance(values, list):
        return []
    result = []
    for item in values:
        if isinstance(item, dict):
            result.append(
                {
                    "priority": str(item.get("priority", "")),
                    "service": str(item.get("service", "")),
                    "reason": str(item.get("reason", "")),
                    "action": str(item.get("action", "")),
                }
            )
        elif isinstance(item, str):
            result.append({"priority": "", "service": "", "reason": item, "action": item})
    return result


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, (str, int, float))]
