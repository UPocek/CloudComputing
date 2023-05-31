import json
import boto3
import os

dynamodb_client = boto3.resource("dynamodb")
users_table = dynamodb_client.Table(os.environ["USERS_TABLE"])
files_table = dynamodb_client.Table(os.environ["FILES_TABLE"])
cognito_client = boto3.client("cognito-idp")


def remove_access(event, context):
    body = json.loads(event["body"])

    if body.get("fileWithAccess") is None or body.get("removeAccessTo") is None:
        return bed_request("Missing required parameters")

    file_name_to_remove_access = body["fileWithAccess"]
    removeUsername = body["removeAccessTo"]

    jwt_token = get_jwt_from_header(event)
    owner = get_user_from_cognito(jwt_token)
    if owner["preferred_username"] == removeUsername:
        return bed_request("Can't remove file from yourself")

    userToRemoveAccess = users_table.get_item(Key={"username": removeUsername})["Item"]
    if not userToRemoveAccess:
        return bed_request("User with given username does not exist")

    remove_access_to_file(
        userToRemoveAccess, owner["preferred_username"], file_name_to_remove_access
    )

    file_to_remove_access_to = files_table.get_item(
        Key={
            "fileName": file_name_to_remove_access,
            "owner": owner["preferred_username"],
        }
    )["Item"]
    file_to_remove_access_to["haveAccess"].remove(removeUsername)
    files_table.put_item(Item=file_to_remove_access_to)

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


def remove_access_to_file(user, owner_username, name_of_file):
    albums = {}
    for key in user["albums"]:
        albums[key] = []
        for userfileName in user["albums"][key]:
            if userfileName != owner_username + "," + name_of_file:
                albums[key].append(userfileName)

    users_table.update_item(
        Key={"username": user["username"]},
        UpdateExpression="SET albums = :albums",
        ExpressionAttributeValues={":albums": albums},
        ReturnValues="UPDATED_NEW",
    )


def bed_request(message):
    return {
        "statusCode": 400,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "DELETE",
        },
        "body": json.dumps({"message": message}),
    }


def successfull(file):
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "DELETE",
        },
        "body": json.dumps(file),
    }
