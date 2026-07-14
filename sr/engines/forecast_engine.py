"""
Forecast Engine

Predicts how the Landing Zone posture changes after remediation.
"""


class ForecastEngine:

    def __init__(self):
        print("Forecast Engine initialized.")

    def generate(self, landing_zone, risk_score):

        print("\n========== ARCHITECT FORECAST ==========\n")

        predicted_risk = risk_score

        if "GuardDuty enabled." not in landing_zone.findings:
            predicted_risk -= 30

        if "Security Hub enabled." not in landing_zone.findings:
            predicted_risk -= 20

        if "CloudTrail enabled." not in landing_zone.findings:
            predicted_risk -= 10

        if predicted_risk < 0:
            predicted_risk = 0

        improvement = risk_score - predicted_risk

        if improvement >= 40:
            trend = "Strong Improvement"

        elif improvement >= 20:
            trend = "Moderate Improvement"

        elif improvement > 0:
            trend = "Minor Improvement"

        else:
            trend = "No Improvement"

        landing_zone.predicted_risk = predicted_risk
        landing_zone.forecast = trend

        print(f"Current Risk Score : {risk_score}")
        print(f"Predicted Risk     : {predicted_risk}")
        print(f"Risk Reduction     : {improvement}")
        print(f"Forecast           : {trend}")

        return predicted_risk