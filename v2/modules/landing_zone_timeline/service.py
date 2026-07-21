"""Compare historical Landing Zone snapshots without owning their persistence."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from v2.modules.landing_zone_timeline.models import TimelineEvent


def build_timeline(snapshots: Iterable[dict[str, Any]]) -> list[TimelineEvent]:
    """Build chronological, evidence-based events from V1/V2 history snapshots."""

    ordered = sorted(
        (snapshot for snapshot in snapshots if _timestamp(snapshot) is not None),
        key=lambda snapshot: _timestamp(snapshot) or datetime.min,
    )
    if not ordered:
        return []

    events = [_baseline_event(ordered[0])]
    for previous, current in zip(ordered, ordered[1:]):
        events.extend(_compare_snapshots(previous, current))
    return sorted(events, key=lambda event: event.timestamp, reverse=True)


def _baseline_event(snapshot: dict[str, Any]) -> TimelineEvent:
    return TimelineEvent(
        timestamp=_timestamp(snapshot) or datetime.min,
        category="Assessment",
        summary="First recorded Landing Zone assessment.",
    )


def _compare_snapshots(previous: dict[str, Any], current: dict[str, Any]) -> list[TimelineEvent]:
    timestamp = _timestamp(current) or datetime.min
    events: list[TimelineEvent] = []

    _append_score_event(events, timestamp, "Overall Health", _overall_score(previous), _overall_score(current), lower_is_better=False)
    _append_score_event(events, timestamp, "Risk Score", _risk_score(previous), _risk_score(current), lower_is_better=True)

    _append_set_events(events, timestamp, "AWS account", previous.get("accounts"), current.get("accounts"))
    _append_set_events(events, timestamp, "AWS region", previous.get("regions"), current.get("regions"))
    _append_set_events(events, timestamp, "Finding", previous.get("findings"), current.get("findings"))

    previous_architecture = _architecture(previous)
    current_architecture = _architecture(current)
    if previous_architecture and current_architecture and previous_architecture != current_architecture:
        events.append(
            TimelineEvent(
                timestamp=timestamp,
                category="Fingerprint",
                summary=f"Architecture rating changed from {previous_architecture} to {current_architecture}.",
                severity="High" if current_architecture in {"Poor", "Critical"} else "Info",
            )
        )
    elif _fingerprint_hash(previous) and _fingerprint_hash(current) and _fingerprint_hash(previous) != _fingerprint_hash(current):
        events.append(TimelineEvent(timestamp, "Fingerprint", "Landing Zone fingerprint changed."))

    return events


def _append_score_event(
    events: list[TimelineEvent],
    timestamp: datetime,
    label: str,
    previous: float | None,
    current: float | None,
    *,
    lower_is_better: bool,
) -> None:
    if previous is None or current is None or previous == current:
        return
    improved = current < previous if lower_is_better else current > previous
    direction = "improved" if improved else "declined"
    severity = "Info" if improved else "High"
    events.append(
        TimelineEvent(
            timestamp=timestamp,
            category=label,
            summary=f"{label} {direction} from {previous:.1f} to {current:.1f}.",
            severity=severity,
        )
    )


def _append_set_events(
    events: list[TimelineEvent],
    timestamp: datetime,
    label: str,
    previous: Any,
    current: Any,
) -> None:
    old_values = _as_set(previous)
    new_values = _as_set(current)
    for value in sorted(new_values - old_values):
        events.append(TimelineEvent(timestamp, label, f"{label} added: {value}."))
    for value in sorted(old_values - new_values):
        events.append(TimelineEvent(timestamp, label, f"{label} removed: {value}.", severity="Medium"))


def _timestamp(snapshot: dict[str, Any]) -> datetime | None:
    value = snapshot.get("timestamp")
    if not isinstance(value, str):
        return None
    for pattern in ("%Y-%m-%d_%H-%M-%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(value, pattern)
        except ValueError:
            continue
    return None


def _overall_score(snapshot: dict[str, Any]) -> float | None:
    value = snapshot.get("overall_score")
    if value is None and isinstance(snapshot.get("fingerprint"), dict):
        value = snapshot["fingerprint"].get("overall")
    return _numeric(value)


def _risk_score(snapshot: dict[str, Any]) -> float | None:
    value = snapshot.get("risk_score")
    if isinstance(value, dict):
        value = value.get("score")
    return _numeric(value)


def _architecture(snapshot: dict[str, Any]) -> str | None:
    value = snapshot.get("architecture")
    if value is None and isinstance(snapshot.get("fingerprint"), dict):
        value = snapshot["fingerprint"].get("architecture")
    return str(value) if value else None


def _fingerprint_hash(snapshot: dict[str, Any]) -> str | None:
    fingerprint = snapshot.get("fingerprint")
    return fingerprint.get("hash") if isinstance(fingerprint, dict) else None


def _as_set(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {str(item) for item in value if isinstance(item, (str, int, float))}


def _numeric(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
