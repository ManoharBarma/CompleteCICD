import boto3
import requests
from datetime import datetime, timedelta

# ========== CONFIG ==========
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/XXXX/XXXX/XXXX"  # Replace with your Slack webhook
AWS_REGION = "us-east-1"
# =============================

# Boto3 clients
ce = boto3.client("ce", region_name=AWS_REGION)
ec2 = boto3.client("ec2", region_name=AWS_REGION)
rds = boto3.client("rds", region_name=AWS_REGION)


def get_costs():
    """Fetch AWS daily and month-to-date costs, and top 5 costly services"""
    today = datetime.utcnow().date()
    start_of_month = today.replace(day=1)
    yesterday = today - timedelta(days=1)

    # Daily cost
    daily_cost = ce.get_cost_and_usage(
        TimePeriod={"Start": str(yesterday), "End": str(today)},
        Granularity="DAILY",
        Metrics=["UnblendedCost"]
    )

    daily_total = float(daily_cost["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"])

    # MTD cost
    mtd_cost = ce.get_cost_and_usage(
        TimePeriod={"Start": str(start_of_month), "End": str(today)},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"]
    )
    mtd_total = float(mtd_cost["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"])

    # Top 5 services (daily)
    services = ce.get_cost_and_usage(
        TimePeriod={"Start": str(yesterday), "End": str(today)},
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}]
    )

    service_costs = []
    for group in services["ResultsByTime"][0]["Groups"]:
        service_name = group["Keys"][0]
        amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
        service_costs.append((service_name, amount))

    top_services = sorted(service_costs, key=lambda x: x[1], reverse=True)[:5]

    return daily_total, mtd_total, top_services


def get_unused_resources():
    """Detect unused resources: stopped EC2, unattached EBS, unassociated Elastic IPs, stopped RDS"""
    unused = []

    # Stopped EC2
    instances = ec2.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["stopped"]}]
    )
    for res in instances["Reservations"]:
        for inst in res["Instances"]:
            unused.append(f"EC2 Instance: {inst['InstanceId']} (stopped)")

    # Unattached EBS
    volumes = ec2.describe_volumes(
        Filters=[{"Name": "status", "Values": ["available"]}]
    )
    for vol in volumes["Volumes"]:
        unused.append(f"EBS Volume: {vol['VolumeId']} (unattached, {vol['Size']} GB)")

    # Unassociated Elastic IPs
    addresses = ec2.describe_addresses()
    for addr in addresses["Addresses"]:
        if "InstanceId" not in addr:
            unused.append(f"Elastic IP: {addr['AllocationId']} (unassociated)")

    # Stopped RDS
    dbs = rds.describe_db_instances()
    for db in dbs["DBInstances"]:
        if db["DBInstanceStatus"] == "stopped":
            unused.append(f"RDS Instance: {db['DBInstanceIdentifier']} (stopped)")

    return unused


def send_to_slack(daily_total, mtd_total, top_services, unused):
    """Send structured report to Slack"""
    message = f"""
📊 *Daily AWS Cost & Unused Resources Report*

💰 *Total Cost (Last 1 Day):* ${daily_total:.2f}
💰 *Month-to-Date Cost:* ${mtd_total:.2f}

🔍 *Top 5 Costly Services (Last 1 Day):*
""" + "\n".join([f"{i+1}. {svc} - ${amt:.2f}" for i, (svc, amt) in enumerate(top_services)]) + """

⚠️ *Unused Resources Detected:*
""" + ("\n".join([f"- {res}" for res in unused]) if unused else "✅ None found!") + """

💡 *Recommendation:* Review unused resources above to save costs.
"""

    payload = {"text": message}
    requests.post(SLACK_WEBHOOK_URL, json=payload)


def lambda_handler(event=None, context=None):
    daily_total, mtd_total, top_services = get_costs()
    unused = get_unused_resources()
    send_to_slack(daily_total, mtd_total, top_services, unused)


if __name__ == "__main__":
    lambda_handler()