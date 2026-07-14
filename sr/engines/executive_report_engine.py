"""
Executive Report Engine

Generates an executive summary for architects and CTOs.
"""


class ExecutiveReportEngine:

    def __init__(self):
        print("Executive Report Engine initialized.")

    def generate(self, landing_zone, risk_score):

        print("\n========== EXECUTIVE REPORT ==========\n")

        health = max(0, 100 - risk_score)

        if health >= 90:
            status = "Excellent"
        elif health >= 75:
            status = "Good"
        elif health >= 50:
            status = "Fair"
        else:
            status = "Critical"

        print(f"Infrastructure Health : {health}%")
        print(f"Architecture Rating   : {status}")
        print(f"Network Score         : {landing_zone.network_score}")
        print(f"IAM Score : {landing_zone.identity_score}")
        print(f"Operations Score      : {landing_zone.operations_score}")

        print("\nExecutive Summary:")

        if risk_score == 0:
            print("Infrastructure is production ready.")
        else:
            print("Infrastructure requires remediation before production.")

        print(f"\nOpen Findings : {len(landing_zone.findings)}")
        print(f"Recommendations : {len(landing_zone.recommendations)}")