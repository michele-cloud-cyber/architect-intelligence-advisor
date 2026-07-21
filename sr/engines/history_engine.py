"""
History Engine

Stores every analysis performed by AIA.
"""

import json
import os
from datetime import datetime
from pathlib import Path


class HistoryEngine:

    def __init__(self, history_directories=None, write_directory=None):
        print("History Engine initialized.")
        self.history_directories = [
            Path(directory) for directory in (history_directories or ["history"])
        ]
        self.write_directory = Path(write_directory) if write_directory else self.history_directories[0]

    def save(self, landing_zone, risk_score):

        os.makedirs(self.write_directory, exist_ok=True)

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

        filename = self.write_directory / f"{timestamp}.json"

        with open(filename, "w") as file:
            json.dump(report, file, indent=4)

        with open(self.write_directory / "last_fingerprint.txt", "w") as file:
            file.write(json.dumps(landing_zone.fingerprint, indent=4))

        print("\nHistory saved:")
        print(filename)

        return str(filename)

    def load_last_report(self):

        reports = self.load_reports()
        if not reports:
            return None
        return reports[-1]

    def load_reports(self):
        """Load valid snapshots from configured directories, oldest first.

        The default remains the legacy ``history`` location. Multiple locations
        are used by the internal application API to preserve V1 archives.
        """

        reports = []
        for directory in self.history_directories:
            if not directory.exists():
                continue
            for filename in sorted(directory.glob("*.json")):
                try:
                    with open(filename, "r") as file:
                        report = json.load(file)
                    if not isinstance(report, dict):
                        continue
                    reports.append(report)
                except (OSError, json.JSONDecodeError):
                    continue

        reports.sort(key=lambda report: str(report.get("timestamp", "")))
        return reports

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
