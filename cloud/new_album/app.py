import json
import boto3
import os

dynamodb_client = boto3.resource("dynamodb")
users_table = dynamodb_client.Table(os.environ["USERS_TABLE"])
cognito_client = boto3.client("cognito-idp")


def new_album(event, context):
    body = json.loads(event["body"])
    new_album_name = body.get("albumName", "").replace(",", "")
    jwt_token = get_jwt_from_header(event)
    user = get_user_from_cognito(jwt_token)

    user = users_table.get_item(Key={"username": user["preferred_username"]})["Item"]
    if user["albums"].get(new_album_name) is not None:
        return bed_request("Album with that name already exists")
    user["albums"][new_album_name] = []
    users_table.put_item(Item=user)

    return successfull_upload(user)


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
            "Access-Control-Allow-Methods": "POST",
        },
        "body": json.dumps({"message": message}),
    }


def successfull_upload(file):
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
        },
        "body": json.dumps(file),
    }
