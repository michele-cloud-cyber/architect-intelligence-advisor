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
            "architecture": landing_zone.fingerprint.get("architecture"),
            "risk_score": risk_score,
            "security_score": landing_zone.security_score,
            "network_score": landing_zone.network_score,
            "iam_score": landing_zone.identity_score,
            "operations_score": landing_zone.operations_score,
            "recommendations": len(landing_zone.recommendations),
            "forecast": landing_zone.forecast
        }

        filename = f"history/{timestamp}.json"

        with open(filename, "w") as file:
            json.dump(report, file, indent=4)

        print("\nHistory saved:")
        print(filename)

        return filename