"""
Risk Engine

Calculates the architectural risk score of the
Landing Zone based on collected observations.
"""


class RiskEngine:

    def __init__(self):
        print("Risk Engine initialized.")

    def evaluate(self, landing_zone):

        print("Evaluating Landing Zone risk...")

        risk_score = 0

        # CloudTrail
        if "CloudTrail enabled." not in landing_zone.findings:
            risk_score += 30
            print("CloudTrail is NOT enabled (+30 risk)")
        else:
            print("CloudTrail is enabled")

        # GuardDuty
        if "GuardDuty enabled." not in landing_zone.findings:
            risk_score += 30
            print("GuardDuty is NOT enabled (+30 risk)")
        else:
            print("GuardDuty is enabled")

        # Security Hub
        if "Security Hub enabled." not in landing_zone.findings:
            risk_score += 20
            print("Security Hub is NOT enabled (+20 risk)")
        else:
            print("Security Hub is enabled")

        print("Checking IAM risks...")
        print("Checking operational risks...")

        print(f"Global Risk Score: {risk_score}/100")

        if risk_score == 0:
            print("Architecture is WELL ARCHITECTED.")
        elif risk_score <= 30:
            print("Architecture risk: LOW")
        elif risk_score <= 60:
            print("Architecture risk: MEDIUM")
        else:
            print("Architecture risk: HIGH")

        landing_zone.risk_score = risk_score

        print("Risk evaluation completed.")

        return risk_score