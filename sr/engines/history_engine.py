"""
History Engine

Stores every analysis performed by AIA.
"""

import json
import os
from datetime import datetime


class HistoryEngine:

    def __init__(self):
        print("History Engine initialized.")

    def save(self, landing_zone, risk_score):

        os.makedirs("history", exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        report = {
            "timestamp": timestamp,
            "organization": getattr(landing_zone, "organization", ""),
            "accounts": getattr(landing_zone, "accounts", []),
            "regions": getattr(landing_zone, "regions", []),

            "architecture": landing_zone.fingerprint.get("architecture"),
            "overall_score": landing_zone.fingerprint.get("overall"),
            "fingerprint": landing_zone.fingerprint,

            "risk_score": risk_score,

            "security_score": landing_zone.security_score,
            "network_score": landing_zone.network_score,
            "iam_score": landing_zone.identity_score,
            "operations_score": landing_zone.operations_score,

            "findings": landing_zone.findings,
            "recommendations": landing_zone.recommendations,
            "forecast": landing_zone.forecast
        }

        filename = f"history/{timestamp}.json"

        with open(filename, "w") as file:
            json.dump(report, file, indent=4)

        with open("history/last_fingerprint.txt", "w") as file:
            file.write(json.dumps(landing_zone.fingerprint, indent=4))

        print("\nHistory saved:")
        print(filename)

        return filename

    def load_last_report(self):

        if not os.path.exists("history"):
            return None

        files = [
            f for f in os.listdir("history")
            if f.endswith(".json")
        ]

        if not files:
            return None

        files.sort()

        latest = files[-1]

        with open(f"history/{latest}", "r") as file:
            return json.load(file)

    def compare(self, current_report):

        previous = self.load_last_report()

        if previous is None:
            return ["First analysis available."]

        changes = []

        previous_score = previous.get("overall_score", 0)
        current_score = current_report.get("overall_score", 0)

        if current_score > previous_score:
            changes.append(
                f"Overall score improved from {previous_score:.1f} to {current_score:.1f}"
            )

        elif current_score < previous_score:
            changes.append(
                f"Overall score decreased from {previous_score:.1f} to {current_score:.1f}"
            )

        previous_risk = previous.get("risk_score", 0)
        current_risk = current_report.get("risk_score", 0)

        if current_risk < previous_risk:
            changes.append("Risk score improved.")

        elif current_risk > previous_risk:
            changes.append("Risk score increased.")

        if len(changes) == 0:
            changes.append("No significant architectural changes detected.")

        return changes