import boto3
import json
import os

ses_client = boto3.client("ses")
dynamodb_client = boto3.resource("dynamodb")
user_table = dynamodb_client.Table(os.environ["USERS_TABLE"])
invitations_table = dynamodb_client.Table(os.environ["INVITATIONS_TABLE"])
lighting_gallery_url = os.environ["BASE_URL"]


def family_invite(event, context):
    body = json.loads(event["body"])
    inviter = body.get("inviter")
    family_member = body.get("family_member")

    if inviter is None or family_member is None:
        return bed_request("Missing required parameters.")

    current_inviter = user_table.get_item(Key={"username": inviter}).get("Item")

    if current_inviter is None:
        return bed_request("Inviter doesn't exist.")

    if current_inviter["email"] == family_invite:
        return bed_request("You can't invite yourself.")

    current_family_member = user_table.get_item(Key={"username": family_member}).get(
        "Item"
    )

    if current_family_member is not None:
        return bed_request("Family member already has account.")

    invitations_table.put_item(
        Item={"id": f"{family_member},{inviter}", "status": "pending"}
    )

    sender_email = "berzaznanjars@gmail.com"
    recipient_email = family_member
    subject = "Invitation to Lighting Gallery"
    body = f'You are invited by {current_inviter["email"]} to join Lighting Gallery. Check it out at {lighting_gallery_url}/registration 🚀'
    response = ses_client.send_email(
        Source=sender_email,
        Destination={"ToAddresses": [recipient_email]},
        Message={"Subject": {"Data": subject}, "Body": {"Text": {"Data": body}}},
    )

    return successfull(response)


def bed_request(message):
    return {
        "statusCode": 400,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
        },
        "body": json.dumps({"message": message}),
    }


def successfull(response):
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
        },
        "body": json.dumps(response),
    }
