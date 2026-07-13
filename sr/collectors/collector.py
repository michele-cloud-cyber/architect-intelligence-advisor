"""
AWS Collector

Collects information from an AWS Landing Zone.
"""

import boto3
from botocore.exceptions import ClientError


class Collector:

    def collect(self, landing_zone):

        print("Starting data collection...")

        # -------------------------
        # AWS Organization
        # -------------------------
        organizations = boto3.client("organizations")

        try:
            response = organizations.describe_organization()

            landing_zone.organization = response["Organization"]["MasterAccountEmail"]

            print(f"Organization: {landing_zone.organization}")

        except ClientError as error:
            print(f"AWS Error: {error}")
            landing_zone.organization = "Example Organization"

        # -------------------------
        # AWS Accounts
        # -------------------------
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

        # -------------------------
        # AWS Regions
        # -------------------------
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

        # -------------------------
        # CloudTrail
        # -------------------------
        cloudtrail = boto3.client("cloudtrail", region_name="eu-west-1")

        try:
            trails = cloudtrail.describe_trails()

            if trails["trailList"]:
                landing_zone.add_finding("CloudTrail enabled.")

                print("CloudTrail Trails:")

                for trail in trails["trailList"]:
                    print(f" - {trail['Name']}")

            else:
                landing_zone.add_finding("CloudTrail not enabled.")

        except ClientError as error:
            print(f"Unable to retrieve CloudTrail information: {error}")
            landing_zone.add_finding("CloudTrail status unknown.")

        # -------------------------
        # GuardDuty
        # -------------------------
        guardduty = boto3.client("guardduty", region_name="eu-west-1")

        try:
            response = guardduty.list_detectors()

            if response["DetectorIds"]:
                landing_zone.add_finding("GuardDuty enabled.")

                print("GuardDuty Detectors:")

                for detector in response["DetectorIds"]:
                    print(f" - {detector}")

            else:
                landing_zone.add_finding("GuardDuty not enabled.")

        except ClientError as error:
            print(f"Unable to retrieve GuardDuty information: {error}")
            landing_zone.add_finding("GuardDuty status unknown.")

        # -------------------------
        # Security Hub
        # -------------------------
        securityhub = boto3.client("securityhub", region_name="eu-west-1")

        try:
            securityhub.describe_hub()

            landing_zone.add_finding("Security Hub enabled.")
            print("Security Hub is enabled.")

        except ClientError as error:
            print(f"Security Hub not available: {error}")
            landing_zone.add_finding("Security Hub not enabled.")