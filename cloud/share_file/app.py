import json
import boto3
import os

dynamodb_client = boto3.resource("dynamodb")
users_table = dynamodb_client.Table(os.environ["USERS_TABLE"])
files_table = dynamodb_client.Table(os.environ["FILES_TABLE"])
cognito_client = boto3.client("cognito-idp")


def share_file(event, context):
    body = json.loads(event["body"])

    if body.get("fileName") is None or body.get("shareWith") is None:
        return bed_request("Missing required parameters")

    shareUsername = body["shareWith"]
    fileNameToShare = body["fileName"]

    jwt_token = get_jwt_from_header(event)
    owner = get_user_from_cognito(jwt_token)
    if owner["preferred_username"] == shareUsername:
        return bed_request("Can't share file with yourself")
    userToShareWith = users_table.get_item(Key={"username": shareUsername})["Item"]
    if not userToShareWith:
        return bed_request("User with given username does not exist")

    userToShareWith["albums"][os.environ["MAIN_ALBUM_NAME"]].append(
        f'{owner["preferred_username"]},{fileNameToShare}'
    )
    users_table.put_item(Item=userToShareWith)
    file_to_share = files_table.get_item(
        Key={"fileName": fileNameToShare, "owner": owner["preferred_username"]}
    )["Item"]
    file_to_share["haveAccess"].append(shareUsername)
    files_table.put_item(Item=file_to_share)

    return successfull(body)


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
