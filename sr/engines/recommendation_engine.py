"""
Recommendation Engine

Generates architectural recommendations based on
analysis results and calculated risks.
"""

class RecommendationEngine:

    def __init__(self):
        print("Recommendation Engine initialized.")

   def generate(self, landing_zone, risk_score):

    print("Generating recommendations...")

    recommendations = []

    if "CloudTrail enabled." not in landing_zone.findings:
        recommendations.append(
            "Enable AWS CloudTrail for auditing and compliance."
        )

    if "GuardDuty enabled." not in landing_zone.findings:
        recommendations.append(
            "Enable Amazon GuardDuty for threat detection."
        )

    if "Security Hub enabled." not in landing_zone.findings:
        recommendations.append(
            "Enable AWS Security Hub to centralize security findings."
        )

    if risk_score >= 60:
        recommendations.append(
            "Perform a full AWS Well-Architected Review."
        )

    print("\nArchitect Recommendations:")

    if recommendations:
        for recommendation in recommendations:
            print(f"- {recommendation}")
    else:
        print("No recommendations. Landing Zone follows best practices.")

    return recommendations
