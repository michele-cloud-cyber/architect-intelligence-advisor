"""Internal application API for Architect Advisor presentation clients."""

from __future__ import annotations

from datetime import datetime
from time import perf_counter
from pathlib import Path
from typing import Any

from sr.engines.history_engine import HistoryEngine
from sr.services.contracts import (
    CapabilityStatus,
    AssessmentSummary,
    DashboardData,
    DashboardFilterOptions,
    DashboardFilters,
    DashboardMetrics,
    DashboardView,
    TrendPoint,
)


class DashboardService:
    """Single application boundary for Streamlit, future REST APIs, or web clients.

    Presentation layers must use this API instead of importing collectors,
    analyzers, engines, Bedrock, or the history repository directly.
    """

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path(__file__).resolve().parents[2]
        self._history_cache: list[dict[str, Any]] | None = None
        self._history_signature: tuple[tuple[str, int, int], ...] | None = None
        self._last_assessment_duration: float | None = None
        self._last_assessment_timestamp: str | None = None
        self.history = HistoryEngine(
            history_directories=[self.project_root / "history", self.project_root / "sr" / "history"]
        )

    def run_assessment(self) -> DashboardData:
        """Run the existing V1 collector/analyzer/engine pipeline unchanged."""

        from sr.services.landing_zone_service import build_landing_zone

        started_at = perf_counter()
        landing_zone = build_landing_zone()
        self._last_assessment_duration = perf_counter() - started_at
        self._history_cache = None
        self._history_signature = None
        reports = self.get_history()
        self._last_assessment_timestamp = str(reports[-1].get("timestamp")) if reports else None
        return self._dashboard_data([self._snapshot_from_landing_zone(landing_zone)], "Current V1 assessment")

    def get_dashboard_data(self, filters: DashboardFilters | None = None) -> DashboardData | None:
        snapshots = self._filter_history(filters)
        return self._dashboard_data(snapshots, "V1 assessment history") if snapshots else None

    def dashboard_data_from_snapshots(self, snapshots: list[dict[str, Any]]) -> DashboardData:
        """Compatibility entry point for callers that already hold V1 snapshots."""

        return self._dashboard_data(snapshots, "V1 assessment history")

    def get_history(self) -> list[dict[str, Any]]:
        """Return every retained V1/V2-compatible snapshot in chronological order."""

        signature = self._current_history_signature()
        if self._history_cache is None or signature != self._history_signature:
            self._history_cache = self.history.load_reports()
            self._history_signature = signature
        return list(self._history_cache)

    def get_filter_options(self) -> DashboardFilterOptions:
        """Expose real organization, account and region values found in history."""

        snapshots = self.get_history()
        organizations = sorted({str(item["organization"]) for item in snapshots if item.get("organization")})
        accounts = sorted(
            {
                str(account)
                for item in snapshots
                for account in (item.get("accounts", []) if isinstance(item.get("accounts"), list) else [])
                if isinstance(account, (str, int, float))
            }
        )
        regions = sorted(
            {
                str(region)
                for item in snapshots
                for region in (item.get("regions", []) if isinstance(item.get("regions"), list) else [])
                if isinstance(region, (str, int, float))
            }
        )
        return DashboardFilterOptions(tuple(organizations), tuple(accounts), tuple(regions))

    def get_dashboard_view(self, filters: DashboardFilters | None = None) -> DashboardView:
        """Return all presentation data for a scope without exposing infrastructure."""

        snapshots = self._filter_history(filters)
        data = self._dashboard_data(snapshots, "V1 assessment history") if snapshots else None
        from v2.modules.fingerprint_engine import build_fingerprint_report
        from v2.modules.forecast_engine import build_forecast_report
        from v2.modules.landing_zone_timeline import build_timeline

        return DashboardView(
            data=data,
            timeline=tuple(build_timeline(snapshots)),
            fingerprint=build_fingerprint_report(snapshots),
            forecast=build_forecast_report(snapshots),
            filtered_snapshot_count=len(snapshots),
        )

    def get_timeline(self, filters: DashboardFilters | None = None):
        from v2.modules.landing_zone_timeline import build_timeline

        return build_timeline(self._filter_history(filters))

    def get_fingerprint_report(self, filters: DashboardFilters | None = None):
        from v2.modules.fingerprint_engine import build_fingerprint_report

        return build_fingerprint_report(self._filter_history(filters))

    def get_forecast_report(self, filters: DashboardFilters | None = None):
        from v2.modules.forecast_engine import build_forecast_report

        return build_forecast_report(self._filter_history(filters))

    def generate_ai_storytelling(self, filters: DashboardFilters | None = None) -> str:
        from v2.modules.ai_storytelling import generate_story

        return generate_story(self._filter_history(filters))

    def generate_demo_storytelling(self, filters: DashboardFilters | None = None) -> str:
        """Create a local evidence summary without using Bedrock or consuming tokens."""

        snapshots = self._filter_history(filters)
        if not snapshots:
            return "No historical assessment is available for the selected scope."
        data = self._dashboard_data(snapshots, "V1 assessment history")
        recommendations = self.get_recommendations(filters)
        strengths = "Overall posture is stable." if data.metrics.overall_health >= 70 else "The current posture requires focused remediation."
        trend = "Insufficient history for a trend." if len(snapshots) < 2 else f"Risk score is currently {data.metrics.risk_score:.0f}/100 across {len(snapshots)} recorded assessments."
        actions = "; ".join(
            str(item.get("action", item.get("reason", "")))
            for item in recommendations[:3]
            if isinstance(item, dict)
        ) or "No structured recommendations are available in the latest V1 snapshot."
        return (
            "### Local assessment narrative\n\n"
            f"**Strengths:** {strengths}\n\n"
            f"**Criticality:** Current risk score is {data.metrics.risk_score:.0f}/100.\n\n"
            f"**Trend:** {trend}\n\n"
            f"**Recommended priorities:** {actions}"
        )

    def get_ai_storytelling_status(self, filters: DashboardFilters | None = None) -> CapabilityStatus:
        available = len(self._filter_history(filters)) >= 2
        return CapabilityStatus(
            "AI Storytelling",
            available,
            "Ready to compare the latest two snapshots." if available else "At least two history snapshots are required.",
        )

    def get_recommendations(self, filters: DashboardFilters | None = None) -> list[Any]:
        latest = self._latest_snapshot(filters)
        recommendations = latest.get("recommendations", []) if latest else []
        return recommendations if isinstance(recommendations, list) else []

    def get_finops_status(self) -> CapabilityStatus:
        return CapabilityStatus("FinOps", False, "FinOps data is not yet produced by the V1 engine.")

    def simulate_what_if(self) -> CapabilityStatus:
        return CapabilityStatus("What-if Simulator", False, "What-if simulation is not implemented yet.")

    def _latest_snapshot(self, filters: DashboardFilters | None = None) -> dict[str, Any] | None:
        history = self._filter_history(filters)
        return history[-1] if history else None

    def _filter_history(self, filters: DashboardFilters | None) -> list[dict[str, Any]]:
        if filters is None:
            return self.get_history()

        def matches(snapshot: dict[str, Any]) -> bool:
            if filters.organization and snapshot.get("organization") != filters.organization:
                return False
            accounts = snapshot.get("accounts", [])
            if filters.account and filters.account not in accounts:
                return False
            regions = snapshot.get("regions", [])
            if filters.region and filters.region not in regions:
                return False
            return True

        return [snapshot for snapshot in self.get_history() if matches(snapshot)]

    def _current_history_signature(self) -> tuple[tuple[str, int, int], ...]:
        signature = []
        for directory in self.history.history_directories:
            if not directory.exists():
                continue
            for path in directory.glob("*.json"):
                try:
                    stat = path.stat()
                    signature.append((str(path), stat.st_mtime_ns, stat.st_size))
                except OSError:
                    continue
        return tuple(sorted(signature))

    def _dashboard_data(self, snapshots: list[dict[str, Any]], source_label: str) -> DashboardData:
        trend = tuple(self._trend_point(snapshot) for snapshot in snapshots)
        latest = snapshots[-1]
        latest_point = trend[-1]
        metrics = DashboardMetrics(
            overall_health=latest_point.overall_health,
            risk_score=latest_point.risk_score,
            finops_score=self._optional_metric(latest, "finops_score"),
            compliance_score=self._optional_metric(latest, "compliance_score"),
        )
        return DashboardData(
            metrics=metrics,
            trend=trend,
            risk_distribution=self._risk_distribution(latest),
            source_label=source_label,
            latest_scan_at=latest_point.timestamp,
            assessment_summary=AssessmentSummary(
                last_assessment=latest_point.timestamp,
                duration_seconds=(
                    self._last_assessment_duration
                    if latest.get("timestamp") == self._last_assessment_timestamp
                    else None
                ),
                accounts_scanned=self._collection_size(latest.get("accounts")),
                regions_scanned=self._collection_size(latest.get("regions")),
            ),
        )

    def _snapshot_from_landing_zone(self, landing_zone: Any) -> dict[str, Any]:
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
            "overall_score": landing_zone.fingerprint.get("overall"),
            "fingerprint": landing_zone.fingerprint,
            "risk_score": landing_zone.risk_score,
            "security_score": landing_zone.security_score,
            "organization": landing_zone.organization,
            "accounts": landing_zone.accounts,
            "regions": landing_zone.regions,
            "findings": landing_zone.findings,
            "recommendations": landing_zone.recommendations,
        }

    def _trend_point(self, snapshot: dict[str, Any]) -> TrendPoint:
        risk_score = self._risk_score(snapshot)
        fingerprint = snapshot.get("fingerprint")
        fingerprint = fingerprint if isinstance(fingerprint, dict) else {}
        overall_score = self._number(snapshot.get("overall_score"), self._number(fingerprint.get("overall"), 100 - risk_score))
        return TrendPoint(
            timestamp=self._timestamp(snapshot["timestamp"]),
            overall_health=self._clamp(overall_score),
            risk_score=self._clamp(risk_score),
        )

    def _risk_distribution(self, snapshot: dict[str, Any]) -> dict[str, int]:
        distribution = {level: 0 for level in ("Critical", "High", "Medium", "Low")}
        supplied = snapshot.get("risk_distribution")
        if isinstance(supplied, dict):
            for level in distribution:
                distribution[level] = int(self._number(supplied.get(level), 0))
            return distribution
        recommendations = snapshot.get("recommendations")
        if not isinstance(recommendations, list):
            return distribution
        for recommendation in recommendations:
            if isinstance(recommendation, dict):
                level = str(recommendation.get("priority", "")).title()
                if level in distribution:
                    distribution[level] += 1
        return distribution

    def _risk_score(self, snapshot: dict[str, Any]) -> float:
        value = snapshot.get("risk_score", 0)
        return self._number(value.get("score", 0) if isinstance(value, dict) else value, 0)

    def _optional_metric(self, snapshot: dict[str, Any], key: str) -> float | None:
        return self._clamp(self._number(snapshot[key], 0)) if snapshot.get(key) is not None else None

    @staticmethod
    def _collection_size(value: Any) -> int | None:
        return len(value) if isinstance(value, list) else None

    @staticmethod
    def _timestamp(value: Any) -> datetime:
        for pattern in ("%Y-%m-%d_%H-%M-%S", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(str(value), pattern)
            except ValueError:
                continue
        return datetime.min

    @staticmethod
    def _number(value: Any, default: float) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(100.0, value))
