"""
AWS Collector

Collects information from an AWS Landing Zone.
"""

import boto3
from botocore.exceptions import ClientError


class Collector:

    def collect(self, landing_zone):

        print("Starting data collection...")

        # Organizations
        organizations = boto3.client("organizations")

        try:
            org = organizations.describe_organization()
            landing_zone.organization = org["Organization"]["MasterAccountEmail"]
            print(f"Organization: {landing_zone.organization}")
        except ClientError as e:
            print(f"Organization error: {e}")
            landing_zone.organization = None

        # Accounts
        try:
            resp = organizations.list_accounts()
            landing_zone.accounts = [a["Name"] for a in resp["Accounts"]]
            print(f"Accounts: {len(landing_zone.accounts)}")
        except ClientError as e:
            print(f"Accounts error: {e}")
            landing_zone.accounts = []

        # Regions
        ec2 = boto3.client("ec2", region_name="eu-south-1")
        try:
            resp = ec2.describe_regions(AllRegions=False)
            landing_zone.regions = [r["RegionName"] for r in resp["Regions"]]
            print(f"Regions: {len(landing_zone.regions)}")
        except ClientError as e:
            print(f"Regions error: {e}")
            landing_zone.regions = []

        # CloudTrail
        cloudtrail = boto3.client("cloudtrail", region_name="eu-south-1")
        try:
            trails = cloudtrail.describe_trails()["trailList"]
            if trails:
                landing_zone.add_finding("CloudTrail enabled.")
            else:
                landing_zone.add_finding("CloudTrail not enabled.")
        except ClientError:
            landing_zone.add_finding("CloudTrail status unknown.")

        # GuardDuty
        guardduty = boto3.client("guardduty", region_name="eu-south-1")
        try:
            detectors = guardduty.list_detectors()["DetectorIds"]
            if detectors:
                landing_zone.add_finding("GuardDuty enabled.")
            else:
                landing_zone.add_finding("GuardDuty not enabled.")
        except ClientError:
            landing_zone.add_finding("GuardDuty status unknown.")

        # Security Hub
        securityhub = boto3.client("securityhub", region_name="eu-south-1")
        try:
            securityhub.describe_hub()
            landing_zone.add_finding("Security Hub enabled.")
        except ClientError:
            landing_zone.add_finding("Security Hub not enabled.")

        # IAM Roles
        iam = boto3.client("iam")
        try:
            resp = iam.list_roles()
            landing_zone.iam_roles = [r["RoleName"] for r in resp["Roles"]]
            landing_zone.add_finding(
                f"IAM Roles discovered: {len(landing_zone.iam_roles)}"
            )
        except ClientError:
            landing_zone.iam_roles = []

        # S3 Buckets
        s3 = boto3.client("s3")
        try:
            resp = s3.list_buckets()
            landing_zone.buckets = [b["Name"] for b in resp["Buckets"]]
            landing_zone.add_finding(
                f"S3 Buckets discovered: {len(landing_zone.buckets)}"
            )
        except ClientError:
            landing_zone.buckets = []

        # EC2 Instances
        try:
            resp = ec2.describe_instances()
            landing_zone.ec2_instances = []
            for reservation in resp["Reservations"]:
                for instance in reservation["Instances"]:
                    landing_zone.ec2_instances.append({
                        "id": instance["InstanceId"],
                        "type": instance["InstanceType"],
                        "state": instance["State"]["Name"],
                    })
        except ClientError:
            landing_zone.ec2_instances = []

        # VPCs
        try:
            resp = ec2.describe_vpcs()
            landing_zone.vpcs = [
                {
                    "id": v["VpcId"],
                    "cidr": v["CidrBlock"],
                }
                for v in resp["Vpcs"]
            ]
        except ClientError:
            landing_zone.vpcs = []

        print("Collection completed.")
        return landing_zone
