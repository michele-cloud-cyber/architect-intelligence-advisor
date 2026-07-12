"""
Architect Intelligence Advisor (AIA)

Application Entry Point
"""

from collectors.collector import Collector
from analyzers.analyzer import Analyzer
from engines.risk_engine import RiskEngine
from engines.recommendation_engine import RecommendationEngine
from models.landing_zone import LandingZone
from utils.logger import Logger


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

    # Calculate risk score
    risk = RiskEngine()
    risk_score = risk.evaluate(landing_zone)

    # Generate recommendations
    recommendation = RecommendationEngine()
    recommendation.generate(landing_zone, risk_score)

    # Print final summary
    landing_zone.summary()

    Logger.info("Application completed successfully")


if __name__ == "__main__":
    main()
