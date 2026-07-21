"""Internal application API for Architect Advisor presentation clients."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from sr.engines.history_engine import HistoryEngine
from sr.services.contracts import CapabilityStatus, DashboardData, DashboardMetrics, TrendPoint


class DashboardService:
    """Single application boundary for Streamlit, future REST APIs, or web clients.

    Presentation layers must use this API instead of importing collectors,
    analyzers, engines, Bedrock, or the history repository directly.
    """

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path(__file__).resolve().parents[2]
        self.history = HistoryEngine(
            history_directories=[self.project_root / "history", self.project_root / "sr" / "history"]
        )

    def run_assessment(self) -> DashboardData:
        """Run the existing V1 collector/analyzer/engine pipeline unchanged."""

        from sr.services.landing_zone_service import build_landing_zone

        landing_zone = build_landing_zone()
        return self._dashboard_data([self._snapshot_from_landing_zone(landing_zone)], "Current V1 assessment")

    def get_dashboard_data(self) -> DashboardData | None:
        snapshots = self.get_history()
        return self._dashboard_data(snapshots, "V1 assessment history") if snapshots else None

    def dashboard_data_from_snapshots(self, snapshots: list[dict[str, Any]]) -> DashboardData:
        """Compatibility entry point for callers that already hold V1 snapshots."""

        return self._dashboard_data(snapshots, "V1 assessment history")

    def get_history(self) -> list[dict[str, Any]]:
        """Return every retained V1/V2-compatible snapshot in chronological order."""

        return self.history.load_reports()

    def get_timeline(self):
        from v2.modules.landing_zone_timeline import build_timeline

        return build_timeline(self.get_history())

    def get_fingerprint_report(self):
        from v2.modules.fingerprint_engine import build_fingerprint_report

        return build_fingerprint_report(self.get_history())

    def get_forecast_report(self):
        from v2.modules.forecast_engine import build_forecast_report

        return build_forecast_report(self.get_history())

    def generate_ai_storytelling(self) -> str:
        from v2.modules.ai_storytelling import generate_story

        return generate_story(self.get_history())

    def get_ai_storytelling_status(self) -> CapabilityStatus:
        available = len(self.get_history()) >= 2
        return CapabilityStatus(
            "AI Storytelling",
            available,
            "Ready to compare the latest two snapshots." if available else "At least two history snapshots are required.",
        )

    def get_recommendations(self) -> list[Any]:
        latest = self._latest_snapshot()
        recommendations = latest.get("recommendations", []) if latest else []
        return recommendations if isinstance(recommendations, list) else []

    def get_finops_status(self) -> CapabilityStatus:
        return CapabilityStatus("FinOps", False, "FinOps data is not yet produced by the V1 engine.")

    def simulate_what_if(self) -> CapabilityStatus:
        return CapabilityStatus("What-if Simulator", False, "What-if simulation is not implemented yet.")

    def _latest_snapshot(self) -> dict[str, Any] | None:
        history = self.get_history()
        return history[-1] if history else None

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
        )

    def _snapshot_from_landing_zone(self, landing_zone: Any) -> dict[str, Any]:
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
            "overall_score": landing_zone.fingerprint.get("overall"),
            "fingerprint": landing_zone.fingerprint,
            "risk_score": landing_zone.risk_score,
            "security_score": landing_zone.security_score,
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
