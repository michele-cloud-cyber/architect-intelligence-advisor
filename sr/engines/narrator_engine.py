"""
Narrator Engine

Generates a human-readable architectural report.
"""


class NarratorEngine:

    def __init__(self):
        print("Narrator Engine initialized.")

    def generate(self, landing_zone):

        print("\n========== DAILY ARCHITECT REPORT ==========\n")

        report = []

        report.append("Today the Landing Zone was analyzed.")

        if "CloudTrail enabled." in landing_zone.findings:
            report.append(
                "CloudTrail is active and audit logging is operational."
            )
        else:
            report.append(
                "CloudTrail is disabled. Audit logging is missing."
            )

        if "GuardDuty enabled." in landing_zone.findings:
            report.append(
                "GuardDuty is monitoring threats across the environment."
            )
        else:
            report.append(
                "GuardDuty is disabled. Threat detection coverage is reduced."
            )

        if "Security Hub enabled." in landing_zone.findings:
            report.append(
                "Security Hub is aggregating security findings."
            )
        else:
            report.append(
                "Security Hub is disabled. Centralized visibility is unavailable."
            )

        architecture = landing_zone.fingerprint.get("architecture", "Unknown")

        report.append(f"Overall architectural posture: {architecture}.")

        report.append(
            "Review the remediation priorities before deploying production workloads."
        )

        landing_zone.daily_report = report

        for line in report:
            print(f"- {line}")

        return report