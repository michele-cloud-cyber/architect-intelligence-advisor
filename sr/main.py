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

    landing_zone = LandingZone()
collector = Collector()
    collector.collect(landing_zone)
    

    analyzer = Analyzer()
    analyzer.analyze()

    risk = RiskEngine()
    risk.evaluate()

    recommendation = RecommendationEngine()
    recommendation.generate()

    landing_zone.summary()

    Logger.info("Application completed successfully")


if __name__ == "__main__":
    main()
