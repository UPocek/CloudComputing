import json
import boto3
import os

dynamodb_client = boto3.resource("dynamodb")
users_table = dynamodb_client.Table(os.environ["USERS_TABLE"])
files_table = dynamodb_client.Table(os.environ["FILES_TABLE"])
cognito_client = boto3.client("cognito-idp")


def share_album(event, context):
    body = json.loads(event["body"])

    if body.get("albumName") is None or body.get("shareWith") is None:
        return bed_request("Missing required parameters")

    share_with_username = body["shareWith"]
    album_name_to_share = body["albumName"]

    jwt_token = get_jwt_from_header(event)
    owner = get_user_from_cognito(jwt_token)

    if owner["preferred_username"] == share_with_username:
        return bed_request("Can't share album with yourself")

    whole_owner = users_table.get_item(Key={"username": owner["preferred_username"]})[
        "Item"
    ]
    if not whole_owner:
        return bed_request("User with given username does not exist")

    if whole_owner["albums"].get(album_name_to_share) is None:
        return bed_request("Can't share album you don't own")

    user_to_share_with = users_table.get_item(Key={"username": share_with_username})[
        "Item"
    ]
    if not user_to_share_with:
        return bed_request("User with given username does not exist")

    if album_name_to_share not in user_to_share_with["albums"].keys():
        user_to_share_with["albums"][album_name_to_share] = []
    for file_name_to_share in whole_owner["albums"][album_name_to_share]:
        if file_name_to_share.split(",")[0] == owner["preferred_username"]:
            user_to_share_with["albums"][album_name_to_share].append(file_name_to_share)
            update_file(
                file_name_to_share.split(",")[1],
                owner["preferred_username"],
                share_with_username,
            )
    users_table.put_item(Item=user_to_share_with)

    return successfull(body)


def update_file(file_name_to_share, owner_username, share_with_username):
    file_to_share = files_table.get_item(
        Key={"fileName": file_name_to_share, "owner": owner_username}
    )["Item"]
    file_to_share["haveAccess"].append(share_with_username)
    files_table.put_item(Item=file_to_share)


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
