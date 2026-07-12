"""
Landing Zone Digital Twin
"""

class LandingZone:

    def __init__(self):

        self.organization = None
        self.accounts = []
        self.regions = []

        self.security_score = 0
        self.network_score = 0
        self.identity_score = 0
        self.operations_score = 0

        self.findings = []

    def add_finding(self, finding):
        self.findings.append(finding)

    def summary(self):

        print("\n========== LANDING ZONE SUMMARY ==========")

        print(f"Security Score : {self.security_score}")
        print(f"Network Score  : {self.network_score}")
        print(f"IAM Score      : {self.identity_score}")
        print(f"Operations     : {self.operations_score}")

        print("\nFindings:")

        if not self.findings:
            print("No findings.")

        for finding in self.findings:
            print(f"- {finding}")
