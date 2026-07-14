"""
Drift Engine

Compares the current Landing Zone fingerprint
with the previous execution.
"""

import os
import hashlib


class DriftEngine:

    def __init__(self):
        print("Drift Engine initialized.")

    def generate(self, landing_zone):

        print("\n========== ARCHITECTURAL DRIFT ==========\n")

        fingerprint = "\n".join(sorted(landing_zone.findings))

        current_hash = hashlib.sha256(
            fingerprint.encode()
        ).hexdigest()

        os.makedirs("history", exist_ok=True)

        fingerprint_file = "history/last_fingerprint.txt"

        if not os.path.exists(fingerprint_file):

            with open(fingerprint_file, "w") as f:
                f.write(current_hash)

            print("First execution.")
            print("No previous architecture available.")

            return

        with open(fingerprint_file, "r") as f:
            previous_hash = f.read()

        if previous_hash == current_hash:

            print("No architectural drift detected.")
            print("Infrastructure unchanged.")

        else:

            print("Architectural Drift detected!")
            print("Landing Zone has changed since last execution.")

            with open(fingerprint_file, "w") as f:
                f.write(current_hash)