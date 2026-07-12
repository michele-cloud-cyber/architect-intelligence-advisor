"""
Landing Zone Digital Twin

Represents the current architectural state of an
AWS Landing Zone.
"""

class LandingZone:

    def __init__(self):
        self.name = "AWS Landing Zone"
        self.security_score = 0
        self.network_score = 0
        self.identity_score = 0
        self.operations_score = 0

    def summary(self):
        print("Landing Zone Digital Twin")
        print(f"Security Score: {self.security_score}")
        print(f"Network Score: {self.network_score}")
        print(f"Identity Score: {self.identity_score}")
        print(f"Operations Score: {self.operations_score}")
