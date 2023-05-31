import boto3
import json

ses_client = boto3.client("ses")


def notify(event, context):
    body = json.loads(event["Records"][0]["Sns"]["Message"])

    for receiver in body["receivers"]:
        sender_email = "berzaznanjars@gmail.com"
        recipient_email = receiver
        subject = body["subject"]
        body = body["content"]
        response = ses_client.send_email(
            Source=sender_email,
            Destination={"ToAddresses": [recipient_email]},
            Message={"Subject": {"Data": subject}, "Body": {"Text": {"Data": body}}},
        )
