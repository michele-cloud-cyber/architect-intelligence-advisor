"""
Risk Engine

Calculates the architectural risk score of the Landing Zone.
"""


class RiskEngine:

    def __init__(self):
        print("Risk Engine initialized.")

    def evaluate(self, landing_zone):

        print("Evaluating Landing Zone risk...")

        risk_score = 0
        findings = []
        recommendations = []

        # ---------------------------------------------------
        # CloudTrail
        # ---------------------------------------------------

        if "CloudTrail enabled." not in landing_zone.findings:
            risk_score += 30
            findings.append("CloudTrail is disabled")
            recommendations.append("Enable AWS CloudTrail in all accounts")
        else:
            print("CloudTrail OK")

        # ---------------------------------------------------
        # GuardDuty
        # ---------------------------------------------------

        if "GuardDuty enabled." not in landing_zone.findings:
            risk_score += 30
            findings.append("GuardDuty is disabled")
            recommendations.append("Enable GuardDuty organization-wide")
        else:
            print("GuardDuty OK")

        # ---------------------------------------------------
        # Security Hub
        # ---------------------------------------------------

        if "Security Hub enabled." not in landing_zone.findings:
            risk_score += 20
            findings.append("Security Hub is disabled")
            recommendations.append("Enable AWS Security Hub")
        else:
            print("Security Hub OK")

        # ---------------------------------------------------
        # IAM
        # ---------------------------------------------------

        print("Checking IAM risks...")

        if getattr(landing_zone, "admin_roles", 0) > 2:
            risk_score += 10
            findings.append("Too many Administrator roles")
            recommendations.append("Apply least privilege to IAM roles")

        # ---------------------------------------------------
        # Operational
        # ---------------------------------------------------

        print("Checking operational risks...")

        if getattr(landing_zone, "unused_resources", False):
            risk_score += 10
            findings.append("Unused AWS resources detected")
            recommendations.append("Remove unused resources")

        # ---------------------------------------------------
        # Normalize Score
        # ---------------------------------------------------

        risk_score = min(risk_score, 100)

        landing_zone.risk_score = risk_score

        print(f"Global Risk Score: {risk_score}/100")

        if risk_score == 0:
            print("Architecture is WELL ARCHITECTED")
        elif risk_score <= 30:
            print("Architecture Risk: LOW")
        elif risk_score <= 60:
            print("Architecture Risk: MEDIUM")
        else:
            print("Architecture Risk: HIGH")

        print("Risk evaluation completed.")

        return {
            "score": risk_score,
            "findings": findings,
            "recommendations": recommendations
        }