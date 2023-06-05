import json
import boto3
import os

dynamodb_client = boto3.resource("dynamodb")
files_table = dynamodb_client.Table(os.environ["FILES_TABLE"])
users_table = dynamodb_client.Table(os.environ["USERS_TABLE"])
cognito_client = boto3.client("cognito-idp")
s3_client = boto3.client("s3")
bucket_name = os.environ["FILES_BUCKET"]


def move_file(event, context):
    body = json.loads(event["body"])
    if (
        body.get("oldAlbum") is None
        or body.get("newAlbum") is None
        or body.get("fileName") is None
    ):
        return bed_request("Required parameters missing")

    old_album = body["oldAlbum"]
    new_album = body["newAlbum"]
    file_name = body["fileName"]
    jwt_token = get_jwt_from_header(event)
    user = get_user_from_cognito(jwt_token)
    user = users_table.get_item(Key={"username": user["preferred_username"]})["Item"]

    if old_album != os.environ["MAIN_ALBUM_NAME"]:
        user["albums"][old_album].remove(file_name)
    user["albums"][new_album].append(file_name)
    users_table.put_item(Item=user)

    return successfull_upload(body)


def get_jwt_from_header(event):
    try:
        auth_header = event["headers"]["authorization"]
    except Exception:
        auth_header = event["headers"]["Authorization"]
    return auth_header.split()[1]


def get_user_from_cognito(jwt):
    user = cognito_client.get_user(AccessToken=jwt)
    current_user = {}

    for attribute in user["UserAttributes"]:
        current_user[attribute["Name"].replace("custom:", "")] = attribute["Value"]
    return current_user


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


def successfull_upload(file):
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "PUT",
        },
        "body": json.dumps(file),
    }
