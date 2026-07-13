"""
Fingerprint Engine

Creates a unique architectural fingerprint for the Landing Zone.
"""

import hashlib


class FingerprintEngine:

    def __init__(self):
        print("Fingerprint Engine initialized.")

    def generate(self, landing_zone):

        print("Generating Landing Zone fingerprint...")

        fingerprint_data = [
            str(landing_zone.findings),
            str(landing_zone.risk_score)
        ]

        raw = "|".join(fingerprint_data)

        fingerprint = hashlib.sha256(raw.encode()).hexdigest()

        landing_zone.fingerprint = fingerprint

        print(f"Fingerprint: {fingerprint[:16]}...")
