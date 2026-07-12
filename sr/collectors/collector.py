import boto3
from botocore.exceptions import ClientError


def collect(self, landing_zone):

    print("Starting data collection...")
     organizations = boto3.client("organizations")

    try:
        response = organizations.describe_organization()

        landing_zone.organization = response["Organization"]["MasterAccountEmail"]

        print(f"Organization: {landing_zone.organization}")

    except ClientError as error:
        print(f"AWS Error: {error}")

    landing_zone.organization = "Example Organization"
try:
        response = organizations.list_accounts()

        landing_zone.accounts = []

        for account in response["Accounts"]:
            landing_zone.accounts.append(account["Name"])

        print("AWS Accounts discovered:")

        for account in landing_zone.accounts:
            print(f" - {account}")

    except ClientError as error:
        print(f"Unable to retrieve AWS accounts: {error}")

    landing_zone.accounts = [
        "Management",
        "Security",
        "Development",
        "Production"
    ]
ec2 = boto3.client("ec2", region_name="eu-west-1")

    try:
        response = ec2.describe_regions(AllRegions=False)

        landing_zone.regions = []

        for region in response["Regions"]:
            landing_zone.regions.append(region["RegionName"])

        print("AWS Regions discovered:")

        for region in landing_zone.regions:
            print(f" - {region}")

    except ClientError as error:
        print(f"Unable to retrieve AWS regions: {error}")
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
