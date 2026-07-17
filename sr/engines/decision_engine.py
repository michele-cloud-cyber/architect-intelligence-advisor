"""
Decision Engine

Produces the final architectural decision based on the
Fingerprint, Risk Score and Recommendations.
"""


class DecisionEngine:

    def __init__(self):
        print("Decision Engine initialized.")

    def generate(self, landing_zone, risk_score):

        print("\n========== ARCHITECT DECISION ==========\n")

        if isinstance(risk_score, dict):
            risk_score = risk_score.get("score", 0)

        architecture = landing_zone.fingerprint.get("architecture", "Unknown")

        if risk_score >= 70:
            decision = "CRITICAL"
        elif risk_score >= 40:
            decision = "WARNING"
        else:
            decision = "HEALTHY"

        print(f"Architecture Rating : {architecture}")
        print(f"Risk Score          : {risk_score}/100")
        print(f"Decision            : {decision}")
        print(f"Recommendations     : {len(landing_zone.recommendations)}")

        landing_zone.decision = decision

        return decision