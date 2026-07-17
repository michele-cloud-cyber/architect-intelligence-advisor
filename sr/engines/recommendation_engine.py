"""
Recommendation Engine

Generates remediation recommendations based on the Landing Zone status.
"""


class RecommendationEngine:

    def __init__(self):
        print("Recommendation Engine initialized.")

    def generate(self, landing_zone, risk_score):

        print("\nGenerating recommendations...")

        print("======================================")
        print("DEBUG RecommendationEngine")
        print("risk_score value :", risk_score)
        print("risk_score type  :", type(risk_score))
        print("======================================")

        # Se arriva un dict lo converte
        if isinstance(risk_score, dict):
            print("Risk score is a dictionary.")

            if "score" in risk_score:
                risk_score = risk_score["score"]
                print("Converted score:", risk_score)
            else:
                print("ERROR: dictionary has no 'score' key")
                raise ValueError("Invalid risk_score dictionary")

        print("Final risk_score :", risk_score)
        print("Final type       :", type(risk_score))

        if not isinstance(risk_score, (int, float)):
            raise TypeError(
                f"risk_score must be numeric. Received {type(risk_score)} -> {risk_score}"
            )

        recommendations = []

        # ---------------------------------------------------
        # CloudTrail
        # ---------------------------------------------------

        if "CloudTrail enabled." not in landing_zone.findings:
            recommendations.append({
                "priority": "HIGH",
                "service": "CloudTrail",
                "reason": "CloudTrail is disabled.",
                "impact": "Audit logs are not available.",
                "action": "Enable AWS CloudTrail across all AWS accounts.",
                "benefit": "+25 Security Score"
            })

        # ---------------------------------------------------
        # GuardDuty
        # ---------------------------------------------------

        if "GuardDuty enabled." not in landing_zone.findings:
            recommendations.append({
                "priority": "HIGH",
                "service": "GuardDuty",
                "reason": "Threat detection is disabled.",
                "impact": "Potential attacks may go undetected.",
                "action": "Enable GuardDuty organization-wide.",
                "benefit": "+20 Security Score"
            })

        # ---------------------------------------------------
        # Security Hub
        # ---------------------------------------------------

        if "Security Hub enabled." not in landing_zone.findings:
            recommendations.append({
                "priority": "HIGH",
                "service": "Security Hub",
                "reason": "Centralized security management is missing.",
                "impact": "Security findings are fragmented.",
                "action": "Enable AWS Security Hub.",
                "benefit": "+15 Governance Score"
            })

        # ---------------------------------------------------
        # Overall Architecture
        # ---------------------------------------------------

        print("CHECKING: risk_score > 60")

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

        print(f"Generated {len(recommendations)} recommendations.")

        return recommendations