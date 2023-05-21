import json
import boto3
import base64
import os

s3_client = boto3.client("s3")
bucket_name = os.environ["FILES_BUCKET"]


def download_file(event, context):
    fileName = event["queryStringParameters"].get("fileName")
    owner = event["queryStringParameters"].get("owner")
    if fileName is None or owner is None:
        return bed_request("Required parameters missing")
    content = base64.b64encode(
        s3_client.get_object(
            Bucket=bucket_name,
            Key=f"{owner}/{fileName}",
        )
        .get("Body")
        .read()
    ).decode("utf-8")

    return successfull({"content": content})


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
