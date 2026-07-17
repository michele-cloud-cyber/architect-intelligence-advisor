class LandingZone:

    def __init__(self):

        # AWS Organization
        self.organization = None
        self.accounts = []
        self.regions = []

        # AWS Resources
        self.buckets = []
        self.iam_roles = []
        self.vpcs = []
        self.ec2_instances = []
        self.lambda_functions = []

        # Scores
        self.security_score = 0
        self.network_score = 0
        self.identity_score = 0
        self.operations_score = 0
        self.risk_score = 0

        # AI
        self.findings = []
        self.recommendations = []
        self.priorities = []
        self.forecast = []

        # Fingerprint
        self.fingerprint = {}

    def add_finding(self, finding):
        self.findings.append(finding)

    def add_recommendation(self, recommendation):
        self.recommendations.append(recommendation)

    def add_priority(self, priority):
        self.priorities.append(priority)

    def summary(self):

        print("\n========== LANDING ZONE SUMMARY ==========")

        print(f"Organization : {self.organization}")
        print(f"Accounts     : {len(self.accounts)}")
        print(f"Regions      : {len(self.regions)}")
        print(f"S3 Buckets   : {len(self.buckets)}")
        print(f"IAM Roles    : {len(self.iam_roles)}")

        print("\nScores")

        print(f"Security     : {self.security_score}")
        print(f"Networking   : {self.network_score}")
        print(f"IAM          : {self.identity_score}")
        print(f"Operations   : {self.operations_score}")
        print(f"Risk         : {self.risk_score}")

        print("\nFindings")

        if not self.findings:
            print("No findings.")
        else:
            for finding in self.findings:
                print(f"- {finding}")

        print("\nRecommendations")

        if not self.recommendations:
            print("No recommendations.")
        else:
            for recommendation in self.recommendations:
                print(f"- {recommendation}")

        print("\nFingerprint")

        print(self.fingerprint)