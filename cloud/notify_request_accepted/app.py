import boto3
import json

ses_client = boto3.client("ses")


def notify_request_accepted(event, context):
    body = json.loads(event["Records"][0]["Sns"]["Message"])
    sender_email = "berzaznanjars@gmail.com"
    recipient_email = body["receiver"]
    subject = body["subject"]
    body = body["content"]
    response = ses_client.send_email(
        Source=sender_email,
        Destination={"ToAddresses": [recipient_email]},
        Message={"Subject": {"Data": subject}, "Body": {"Text": {"Data": body}}},
    )
