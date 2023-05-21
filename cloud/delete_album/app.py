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
        or path_parameters.get("albumName") == os.environ["MAIN_ALBUM_NAME"]
    ):
        return bed_request("Missing required parameters")

    album_name_to_delete = path_parameters["albumName"]

    jwt_token = get_jwt_from_header(event)
    owner_of_the_file = get_user_from_cognito(jwt_token)
    owner_of_the_file = users_table.get_item(
        Key={"username": owner_of_the_file["preferred_username"]}
    )["Item"]

    if owner_of_the_file["albums"].get(album_name_to_delete) is None:
        return bed_request("Album with that name does not exist")

    files_to_delete = owner_of_the_file["albums"][album_name_to_delete]
    del owner_of_the_file["albums"][album_name_to_delete]
    users_table.put_item(Item=owner_of_the_file)

    for file in files_to_delete:
        file_owner_username, fileName = file.split(",")
        if file_owner_username == owner_of_the_file["username"]:
            delete_one_file(fileName, owner_of_the_file, album_name_to_delete)

    return successfull_album_delete(owner_of_the_file)


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


def delete_one_file(fileName, owner, album_name_to_delete):
    file_to_delete = files_table.get_item(
        Key={"fileName": fileName, "owner": owner["username"]}
    ).get("Item")
    if file_to_delete is None:
        return bed_request("File doesn't exist")

    users = file_to_delete["haveAccess"]
    delete_file_in_users(owner, users, fileName, album_name_to_delete)
    delete_dynamodb(owner, fileName)
    return delete_s3(owner, fileName)


def delete_file_in_users(owner, users, fileName, album_name_to_delete):
    for username in users:
        if username == owner["username"]:
            user = owner
        else:
            user = users_table.get_item(Key={"username": username}).get("Item")
        albums = {}
        for key in user["albums"]:
            if key == album_name_to_delete and username == owner["username"]:
                continue
            albums[key] = []
            for userfileName in user["albums"][key]:
                if userfileName != owner["username"] + "," + fileName:
                    albums[key].append(userfileName)

        users_table.update_item(
            Key={"username": username},
            UpdateExpression="SET albums = :albums",
            ExpressionAttributeValues={":albums": albums},
            ReturnValues="UPDATED_NEW",
        )


def delete_dynamodb(owner, fileName):
    files_table.delete_item(Key={"fileName": fileName, "owner": owner["username"]})


def delete_s3(owner, fileName):
    s3_client.delete_object(
        Bucket=files_bucket_name,
        Key=f"{owner['username']}/{fileName}",
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


def successfull_album_delete(file):
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
        },
        "body": json.dumps(file),
    }
