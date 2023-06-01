import json
import boto3
import os

dynamodb_client = boto3.resource("dynamodb")
invitations_table = dynamodb_client.Table(os.environ["INVITATIONS_TABLE"])


def resolve_invitation(event, context):
    body = json.loads(event["body"])

    if body.get("action") is None or body.get("invite") is None:
        return bed_request("Missing required parameters")

    if body.get("action") != "accept" and body.get("action") != "deny":
        return bed_request("Missing required parameters")

    invitation = invitations_table.get_item(Key={"id": body["invite"]})
    invitation["status"] = body["action"]
    invitations_table.put_item(invitation)

    return successfull(body)


def bed_request(message):
    return {
        "statusCode": 400,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "PUT",
        },
        "body": json.dumps({"message": message}),
    }


def successfull(file):
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "PUT",
        },
        "body": json.dumps(file),
    }
