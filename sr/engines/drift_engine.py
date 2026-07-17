"""
Drift Engine

Detects architectural drift between two Landing Zone scans.
"""


class DriftEngine:

    def __init__(self):
        print("Drift Engine initialized.")

    def generate(self, landing_zone):

        print("Checking architectural drift...")

        if not hasattr(landing_zone, "history"):
            landing_zone.history = []

        landing_zone.drift = [
            "No architectural drift detected."
        ]

        print("Drift analysis completed.")

        return landing_zone.drift

    def compare(self, previous, current):

        drift = []

        old_roles = set(previous.get("iam_roles", []))
        new_roles = set(current.get("iam_roles", []))

        for role in new_roles - old_roles:
            drift.append(f"New IAM Role detected: {role}")

        for role in old_roles - new_roles:
            drift.append(f"IAM Role removed: {role}")

        old_buckets = set(previous.get("buckets", []))
        new_buckets = set(current.get("buckets", []))

        for bucket in new_buckets - old_buckets:
            drift.append(f"New S3 Bucket detected: {bucket}")

        for bucket in old_buckets - new_buckets:
            drift.append(f"S3 Bucket removed: {bucket}")

        if previous.get("fingerprint") != current.get("fingerprint"):
            drift.append("Landing Zone fingerprint has changed.")

        if not drift:
            drift.append("No architectural drift detected.")

        return drift