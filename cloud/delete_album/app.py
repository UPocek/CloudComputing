import json
import boto3
import os
import time

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
    owner_of_the_album = get_user_from_cognito(jwt_token)
    owner_of_the_album = users_table.get_item(
        Key={"username": owner_of_the_album["preferred_username"]}
    )["Item"]

    if owner_of_the_album["albums"].get(album_name_to_delete) is None:
        return bed_request("Album with that name does not exist")

    album_to_delete = owner_of_the_album["albums"][album_name_to_delete]
    del owner_of_the_album["albums"][album_name_to_delete]
    users_table.put_item(Item=owner_of_the_album)

    files_remain = [file for file in album_to_delete]
    for file in album_to_delete:
        file_owner_username, file_name = file.split(",")
        if file_owner_username == owner_of_the_album["username"]:
            try:
                delete_one_file(file_name, file_owner_username, owner_of_the_album)
            except Exception as e:
                print(f"[ERROR]-DeleteAlbum: {e}")
                rollback_album_delete(
                    owner_of_the_album, album_name_to_delete, files_remain
                )
                return server_error("Service unvailable.")
        else:
            try:
                file_meta_data = files_table.get_item(
                    Key={"fileName": file_name, "owner": file_owner_username}
                ).get("Item")
                file_meta_data["haveAccess"].remove(owner_of_the_album["username"])
                files_table.put_item(Item=file_meta_data)
            except Exception as e:
                print(f"[ERROR]-DeleteAlbum: {e}")
                rollback_album_delete(
                    owner_of_the_album, album_name_to_delete, files_remain
                )
                return server_error("Service unvailable.")

            try:
                user = users_table.get_item(
                    Key={"username": owner_of_the_album["username"]}
                ).get("Item")
                albums = {}
                for key in user["albums"]:
                    albums[key] = []
                    for users_file_name in user["albums"][key]:
                        if users_file_name != file_owner_username + "," + file_name:
                            albums[key].append(users_file_name)
                users_table.update_item(
                    Key={"username": owner_of_the_album["username"]},
                    UpdateExpression="SET albums = :albums",
                    ExpressionAttributeValues={":albums": albums},
                    ReturnValues="UPDATED_NEW",
                ).get("Attributes")
            except Exception as e:
                print(f"[ERROR]-DeleteAlbum: {e}")
                rollback_album_delete(
                    owner_of_the_album, album_name_to_delete, files_remain
                )
                rollback_file_metadata(file_meta_data, owner_of_the_album)
                return server_error("Service unvailable.")
        files_remain.remove(file)

    return successfull_album_delete(owner_of_the_album)


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


def rollback_album_delete(owner_of_the_file, album_name_to_delete, files_remain):
    owner_of_the_file["albums"][album_name_to_delete] = files_remain
    users_table.put_item(Item=owner_of_the_file)


def rollback_file_metadata(file_meta_data, owner_of_the_file):
    file_meta_data["haveAccess"].remove(owner_of_the_file["username"])
    files_table.put_item(Item=file_meta_data)


def delete_one_file(file_name, file_owner_username, owner):
    file_to_delete = files_table.get_item(
        Key={"fileName": file_name, "owner": owner["username"]}
    )["Item"]
    if file_to_delete is None:
        return bed_request("File doesn't exist")

    users = file_to_delete["haveAccess"]
    updated_users = delete_file_in_users(file_owner_username, users, file_name)
    file_meta_data = delete_file_metadata(owner, file_name, updated_users)
    return delete_from_persistent_storage(
        owner, file_name, updated_users, file_meta_data
    )


def delete_file_in_users(owner, users, file_name):
    updated_users = []

    try:
        for username in users:
            user = users_table.get_item(Key={"username": username}).get("Item")

            albums = {}
            for key in user["albums"]:
                albums[key] = []
                for user_file_name in user["albums"][key]:
                    if user_file_name != owner + "," + file_name:
                        albums[key].append(user_file_name)

            users_table.update_item(
                Key={"username": username},
                UpdateExpression="SET albums = :albums",
                ExpressionAttributeValues={":albums": albums},
                ReturnValues="UPDATED_NEW",
            ).get("Attributes")
            updated_users.append(user)
    except Exception as e:
        print(f"[ERROR]-Delete: {e}")
        time.sleep(3)
        rollback_updated_users(updated_users, file_name)
        raise Exception("Album delete failed")
    return updated_users


def delete_file_metadata(owner, file_name, updated_users):
    try:
        file_meta_data = files_table.get_item(
            Key={"fileName": file_name, "owner": owner["username"]}
        )
        files_table.delete_item(Key={"fileName": file_name, "owner": owner["username"]})
    except Exception as e:
        print(f"[ERROR]-Delete: {e}")
        rollback_updated_users(updated_users, file_name)
        raise Exception("Album delete failed")
    return file_meta_data


def delete_from_persistent_storage(owner, file_name, updated_users, file_meta_data):
    try:
        return s3_client.delete_object(
            Bucket=files_bucket_name,
            Key=f"{owner['username']}/{file_name}",
        ).get("DeleteMarker", False)
    except Exception as e:
        print(f"[ERROR]-Delete: {e}")
        rollback_updated_users(updated_users, file_name)
        rollback_deleted_file_meta_data(file_meta_data)
        raise Exception("Album delete failed")


def rollback_deleted_file_meta_data(file_meta_data):
    files_table.put_item(Item=file_meta_data)


def rollback_updated_users(updated_users, file_name):
    try:
        for user in updated_users:
            users_table.put_item(Item=user)
    except Exception:
        for user in updated_users:
            print(f"[ERROR]-DeleteRollback: {user['username']} {file_name} ")


def server_error(message):
    return {
        "statusCode": 503,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "DELETE",
        },
        "body": json.dumps({"message": message}),
    }


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


def successfull_album_delete(file):
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "DELETE",
        },
        "body": json.dumps(file),
    }
