"""
Fingerprint Engine

Creates a unique architectural fingerprint
for the Landing Zone.
"""

import hashlib
import json


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

        # -------------------------
        # Security
        # -------------------------

        if "GuardDuty enabled." in findings:
            fingerprint["security"] += 40

        if "Security Hub enabled." in findings:
            fingerprint["security"] += 40

        # -------------------------
        # Logging
        # -------------------------

        if "CloudTrail enabled." in findings:
            fingerprint["logging"] = 100

        # -------------------------
        # IAM maturity
        # -------------------------

        iam_roles = len(getattr(landing_zone, "iam_roles", []))

        if iam_roles > 0:
            fingerprint["identity"] += 10

        if iam_roles > 50:
            fingerprint["identity"] -= 10

        # -------------------------
        # Storage maturity
        # -------------------------

        bucket_count = len(getattr(landing_zone, "buckets", []))

        if bucket_count > 0:
            fingerprint["architecture"] = "Managed Storage"

        # -------------------------
        # Overall Score
        # -------------------------

        overall = (
            fingerprint["security"] +
            fingerprint["networking"] +
            fingerprint["identity"] +
            fingerprint["governance"] +
            fingerprint["logging"]
        ) / 5

        fingerprint["overall"] = overall

        # -------------------------
        # Architecture Rating
        # -------------------------

        if overall >= 90:
            fingerprint["architecture"] = "Excellent"
        elif overall >= 75:
            fingerprint["architecture"] = "Good"
        elif overall >= 60:
            fingerprint["architecture"] = "Fair"
        else:
            fingerprint["architecture"] = "Poor"

        # -------------------------
        # Generate unique fingerprint hash
        # -------------------------

        payload = json.dumps(
            fingerprint,
            sort_keys=True
        )

        fingerprint["hash"] = hashlib.sha256(
            payload.encode()
        ).hexdigest()

        # -------------------------
        # Save inside Landing Zone
        # -------------------------

        landing_zone.security_score = fingerprint["security"]
        landing_zone.network_score = fingerprint["networking"]
        landing_zone.identity_score = fingerprint["identity"]
        landing_zone.operations_score = fingerprint["governance"]

        landing_zone.fingerprint = fingerprint

        print("Fingerprint generated.")
        print(f"Overall Fingerprint Score: {overall:.1f}")
        print(f"Architecture Rating: {fingerprint['architecture']}")
        print(f"Fingerprint Hash: {fingerprint['hash']}")

        return fingerprint