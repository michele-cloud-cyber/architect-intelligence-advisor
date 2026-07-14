"""
Architect Intelligence Advisor (AIA)

Application Entry Point
"""
from engines.priority_engine import PriorityEngine
from collectors.collector import Collector
from analyzers.analyzer import Analyzer
from engines.risk_engine import RiskEngine
from engines.recommendation_engine import RecommendationEngine
from engines.fingerprint_engine import FingerprintEngine
from models.landing_zone import LandingZone
from engines.narrator_engine import NarratorEngine
from engines.forecast_engine import ForecastEngine
from engines.history_engine import HistoryEngine
from engines.drift_engine import DriftEngine
from engines.executive_report_engine import ExecutiveReportEngine


from utils.logger import Logger
from engines.decision_engine import DecisionEngine


def main():

    Logger.info("Starting Architect Intelligence Advisor")

    # Create Landing Zone object
    landing_zone = LandingZone()

    # Collect AWS data
    collector = Collector()
    collector.collect(landing_zone)

    # Analyze architecture
    analyzer = Analyzer()
    analyzer.analyze(landing_zone)

    # Generate fingerprint
    fingerprint = FingerprintEngine()
    fingerprint.generate(landing_zone)
    priority = PriorityEngine()
    priority.generate(landing_zone)

    # Calculate risk score
    risk = RiskEngine()
    risk_score = risk.evaluate(landing_zone)

    # Generate recommendations
    recommendation = RecommendationEngine()
    recommendation.generate(landing_zone, risk_score)
    decision = DecisionEngine()
    decision.generate(landing_zone, risk_score)
    narrator = NarratorEngine()
    narrator.generate(landing_zone)
    forecast = ForecastEngine()
    forecast.generate(landing_zone, risk_score)
    history = HistoryEngine()
    history.save(landing_zone, risk_score)

    drift = DriftEngine()
    drift.generate(landing_zone)

    executive = ExecutiveReportEngine()
    executive.generate(landing_zone, risk_score)


    # Print summary
    landing_zone.summary()

    Logger.info("Application completed successfully")


if __name__ == "__main__":
    main()