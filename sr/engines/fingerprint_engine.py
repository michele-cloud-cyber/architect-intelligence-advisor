"""
Fingerprint Engine

Creates a unique architectural fingerprint
for the Landing Zone.
"""


class FingerprintEngine:

    def __init__(self):
        print("Fingerprint Engine initialized.")

    def generate(self, landing_zone):

        print("Generating Landing Zone fingerprint...")

        findings = landing_zone.findings

        fingerprint = {
            "security": 0,
            "networking": 80,
            "identity": 75,
            "governance": 70,
            "logging": 0,
            "architecture": "Unknown"
        }

        # Security
        if "GuardDuty enabled." in findings:
            fingerprint["security"] += 40

        if "Security Hub enabled." in findings:
            fingerprint["security"] += 40

        # Logging
        if "CloudTrail enabled." in findings:
            fingerprint["logging"] = 100

        overall = (
            fingerprint["security"] +
            fingerprint["networking"] +
            fingerprint["identity"] +
            fingerprint["governance"] +
            fingerprint["logging"]
        ) / 5

        fingerprint["overall"] = overall

        if overall >= 90:
            fingerprint["architecture"] = "Excellent"
        elif overall >= 75:
            fingerprint["architecture"] = "Good"
        elif overall >= 60:
            fingerprint["architecture"] = "Fair"
        else:
            fingerprint["architecture"] = "Poor"

        landing_zone.fingerprint = fingerprint

        print("Fingerprint generated.")
        print(f"Overall Fingerprint Score: {overall:.1f}")
        print(f"Architecture Rating: {fingerprint['architecture']}")

        return fingerprint