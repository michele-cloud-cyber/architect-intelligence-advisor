def collect(self, landing_zone):

    print("Starting data collection...")

    landing_zone.organization = "Example Organization"

    landing_zone.accounts = [
        "Management",
        "Security",
        "Development",
        "Production"
    ]

    landing_zone.regions = [
        "eu-west-1",
        "eu-central-1"
    ]

    landing_zone.add_finding(
        "CloudTrail enabled."
    )

    landing_zone.add_finding(
        "GuardDuty enabled."
    )

    landing_zone.add_finding(
        "Security Hub enabled."
    )

    print("Collection completed.")
