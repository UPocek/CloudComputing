import json
import boto3
import os

dynamodb_client = boto3.resource("dynamodb")
invitations_table = dynamodb_client.Table(os.environ["INVITATIONS_TABLE"])
base_url = os.environ["BASE_URL"]


def resolve_invitation(event, context):
    body = event["body"]

    invitations_table


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


def successfull(file):
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
        },
        "body": json.dumps(file),
    }
