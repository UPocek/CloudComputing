import json
import boto3
import os

dynamodb_client = boto3.resource("dynamodb")
users_table = dynamodb_client.Table(os.environ["USERS_TABLE"])
cognito_client = boto3.client("cognito-idp")
s3_client = boto3.client("s3")
files_bucket_name = os.environ["FILES_BUCKET"]
files_table = dynamodb_client.Table(os.environ["FILES_TABLE"])


def delete_album(event, context):
    path_parameters = event.get("pathParameters")
    if (
        path_parameters is None
        or path_parameters.get("albumName") is None
        or path_parameters.get("albumName") == os.environ["Main Album"]
    ):
        return bed_request("Missing required parameters")
    album_to_delete = path_parameters["albumName"]

    jwt_token = get_jwt_from_header(event)
    user = get_user_from_cognito(jwt_token)
    user = users_table.get_item(Key={"username": user["preferred_username"]})["Item"]

    if user["albums"].get(album_to_delete) is None:
        return bed_request("Album with that name does not exist")

    for file in user["albums"][album_to_delete]:
        owner, fileName = file.split(",")
        if owner != user["username"]:
            delete_someones_file(fileName, owner)
        else:
            delete_this_user_file()

    del user["albums"][album_to_delete]
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


def delete_this_user_file():
    pass


def delete_someones_file(fileName, owner):
    file_to_delete = files_table.get_item(
        Key={"fileName": fileName, "owner": owner}
    ).get("Item")
    if file_to_delete is None:
        return bed_request("File doesn't exist")

    users = file_to_delete["haveAccess"]
    delete_file_in_users(owner, users, fileName)
    delete_dynamodb(owner, fileName)
    return delete_s3(owner, fileName)


def delete_file_in_users(owner, users, fileName):
    for username in users:
        user = users_table.get_item(Key={"username": username}).get("Item")
        albums = {}
        for key in user["albums"]:
            albums[key] = []
            for userfileName in user["albums"][key]:
                if userfileName != owner + "," + fileName:
                    albums[key].append(userfileName)

        users_table.update_item(
            Key={"username": username},
            UpdateExpression="SET albums = :albums",
            ExpressionAttributeValues={":albums": albums},
            ReturnValues="UPDATED_NEW",
        ).get("Attributes")


def delete_dynamodb(owner, fileName):
    files_table.delete_item(Key={"fileName": fileName, "owner": owner})


def delete_s3(owner, fileName):
    s3_client.delete_object(
        Bucket=files_bucket_name,
        Key=f"{owner}/{fileName}",
    )


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
