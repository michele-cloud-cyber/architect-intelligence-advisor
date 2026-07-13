"""
Recommendation Engine

Generates recommendations based on the architectural risk score.
"""


class RecommendationEngine:

    def __init__(self):
        print("Recommendation Engine initialized.")

    def generate(self, landing_zone, risk_score):

        print("Generating recommendations...")

        recommendations = []

        if "CloudTrail enabled." not in landing_zone.findings:
            recommendations.append(
                "Enable AWS CloudTrail across all AWS accounts."
            )

        if "GuardDuty enabled." not in landing_zone.findings:
            recommendations.append(
                "Enable Amazon GuardDuty in every AWS Region."
            )

        if "Security Hub enabled." not in landing_zone.findings:
            recommendations.append(
                "Enable AWS Security Hub."
            )

        if risk_score > 60:
            recommendations.append(
                "Perform a complete Well-Architected Review."
            )

        landing_zone.recommendations = recommendations

        print("Recommendations generated.")

        for recommendation in recommendations:
            print(f"- {recommendation}")