import json
import boto3
import os

dynamodb_client = boto3.resource("dynamodb")
users_table = dynamodb_client.Table(os.environ["USERS_TABLE"])
files_table = dynamodb_client.Table(os.environ["FILES_TABLE"])
cognito_client = boto3.client("cognito-idp")


def user_details(event, context):
    jwt_token = get_jwt_from_header(event)
    user = get_user_from_cognito(jwt_token)

    user = users_table.get_item(Key={"username": user["preferred_username"]})["Item"]

    for albumName in user["albums"]:
        files = []
        for file_name in user["albums"][albumName]:
            owner, name = file_name.split(",")
            file = files_table.get_item(Key={"fileName": name, "owner": owner})["Item"]
            files.append(file)
        user["albums"][albumName] = files

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
