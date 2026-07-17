from sr.models.landing_zone import LandingZone

from sr.collectors.collector import Collector
from sr.analyzers.analyzer import Analyzer

from sr.engines.fingerprint_engine import FingerprintEngine
from sr.engines.priority_engine import PriorityEngine
from sr.engines.risk_engine import RiskEngine
from sr.engines.recommendation_engine import RecommendationEngine
from sr.engines.decision_engine import DecisionEngine
from sr.engines.narrator_engine import NarratorEngine
from sr.engines.forecast_engine import ForecastEngine
from sr.engines.history_engine import HistoryEngine
from sr.engines.drift_engine import DriftEngine
from sr.engines.executive_report_engine import ExecutiveReportEngine


def build_landing_zone():

    print("BUILD LANDING ZONE START")

    landing_zone = LandingZone()

    # Collect AWS data
    Collector().collect(landing_zone)

    # Analyze Landing Zone
    Analyzer().analyze(landing_zone)

    # Generate fingerprint
    FingerprintEngine().generate(landing_zone)

    # Priorities
    PriorityEngine().generate(landing_zone)

    # Risk evaluation
    risk_result = RiskEngine().evaluate(landing_zone)

    print("DEBUG risk_result:", type(risk_result), risk_result)

    risk_score = risk_result["score"]

    print("DEBUG risk_score:", type(risk_score), risk_score)

    landing_zone.risk_findings = risk_result["findings"]
    landing_zone.risk_recommendations = risk_result["recommendations"]

    print(">>> BEFORE RecommendationEngine")
    print("risk_score value:", risk_score)
    print("risk_score type :", type(risk_score))

    # Recommendations
    RecommendationEngine().generate(
        landing_zone,
        risk_score
    )

    print(">>> AFTER RecommendationEngine")

    # Decisions
    DecisionEngine().generate(
        landing_zone,
        risk_score
    )

    # AI Narrator
    NarratorEngine().generate(landing_zone)

    # Forecast
    ForecastEngine().generate(
        landing_zone,
        risk_score
    )

    # History
    HistoryEngine().save(
        landing_zone,
        risk_score
    )

    # Drift
    DriftEngine().generate(landing_zone)

    # Executive report
    ExecutiveReportEngine().generate(
        landing_zone,
        risk_score
    )

    return landing_zone