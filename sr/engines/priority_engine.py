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

            if "GuardDuty not enabled." in finding:
                priorities.append({
                    "priority": "HIGH",
                    "service": "GuardDuty",
                    "action": "Enable GuardDuty"
                })

            elif "Security Hub not enabled." in finding:
                priorities.append({
                    "priority": "HIGH",
                    "service": "Security Hub",
                    "action": "Enable Security Hub"
                })

            elif "CloudTrail not enabled." in finding:
                priorities.append({
                    "priority": "CRITICAL",
                    "service": "CloudTrail",
                    "action": "Enable CloudTrail"
                })

        landing_zone.priorities = priorities

        print("\n========== PRIORITIES ==========")

        if not priorities:
            print("No priorities detected.")
        else:
            for item in priorities:
                print(
                    f"[{item['priority']}] "
                    f"{item['service']} -> {item['action']}"
                )

        return priorities