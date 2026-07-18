"""
Priority Engine

Determines remediation priorities
based on findings.
"""


class PriorityEngine:

    def __init__(self):
        print("Priority Engine initialized.")

    def generate(self, landing_zone):

        print("Calculating remediation priorities...")

        priorities = []

        for finding in landing_zone.findings:

            # ---------------------------------------------------
            # CloudTrail
            # ---------------------------------------------------

            if (
                "CloudTrail not enabled." in finding
                or "CloudTrail is disabled" in finding
            ):

                priorities.append({
                    "priority": "CRITICAL",
                    "service": "CloudTrail",
                    "action": "Enable Organization CloudTrail"
                })

            # ---------------------------------------------------
            # GuardDuty
            # ---------------------------------------------------

            elif (
                "GuardDuty not enabled." in finding
                or "GuardDuty is disabled" in finding
            ):

                priorities.append({
                    "priority": "HIGH",
                    "service": "GuardDuty",
                    "action": "Enable GuardDuty delegated administrator"
                })

            # ---------------------------------------------------
            # Security Hub
            # ---------------------------------------------------

            elif (
                "Security Hub not enabled." in finding
                or "Security Hub is disabled" in finding
            ):

                priorities.append({
                    "priority": "MEDIUM",
                    "service": "Security Hub",
                    "action": "Enable AWS Security Hub"
                })

        landing_zone.priorities = priorities

        print("\n========== PRIORITY CENTER ==========\n")

        if not priorities:
            print("No remediation priorities detected.")
        else:
            for item in priorities:
                print(
                    f"[{item['priority']}] "
                    f"{item['service']} -> {item['action']}"
                )

        return priorities