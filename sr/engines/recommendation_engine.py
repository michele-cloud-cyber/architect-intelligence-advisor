"""
Recommendation Engine

Generates remediation recommendations based on the Landing Zone status.
"""


class RecommendationEngine:

    def __init__(self):
        print("Recommendation Engine initialized.")

    def generate(self, landing_zone, risk_score):

        print("\nGenerating recommendations...")

        recommendations = []

        if "CloudTrail enabled." not in landing_zone.findings:
            recommendations.append({
                "priority": "HIGH",
                "service": "CloudTrail",
                "reason": "CloudTrail is disabled.",
                "impact": "Audit logs are not available.",
                "action": "Enable CloudTrail across all AWS accounts.",
                "benefit": "+25 Security Score"
            })

        if "GuardDuty enabled." not in landing_zone.findings:
            recommendations.append({
                "priority": "HIGH",
                "service": "GuardDuty",
                "reason": "Threat detection is disabled.",
                "impact": "Potential attacks may go undetected.",
                "action": "Enable GuardDuty in all AWS Regions.",
                "benefit": "+20 Security Score"
            })

        if "Security Hub enabled." not in landing_zone.findings:
            recommendations.append({
                "priority": "HIGH",
                "service": "Security Hub",
                "reason": "Centralized security management is missing.",
                "impact": "Security findings are fragmented.",
                "action": "Enable AWS Security Hub.",
                "benefit": "+15 Governance Score"
            })

        if risk_score > 60:
            recommendations.append({
                "priority": "MEDIUM",
                "service": "AWS Well-Architected",
                "reason": "Overall architectural risk is high.",
                "impact": "Architecture may not follow AWS best practices.",
                "action": "Perform a complete AWS Well-Architected Review.",
                "benefit": "Improve overall architecture quality"
            })

        landing_zone.recommendations = recommendations

        print("\n================ RECOMMENDATIONS ================\n")

        if not recommendations:
            print("No recommendations generated.")

        else:
            for index, rec in enumerate(recommendations, start=1):
                print(f"Recommendation #{index}")
                print(f"Priority : {rec['priority']}")
                print(f"Service  : {rec['service']}")
                print(f"Reason   : {rec['reason']}")
                print(f"Impact   : {rec['impact']}")
                print(f"Action   : {rec['action']}")
                print(f"Benefit  : {rec['benefit']}")
                print("-" * 50)

        print(f"\nTotal recommendations: {len(recommendations)}")

        return recommendations