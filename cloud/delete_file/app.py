import json
import boto3
import os
import time

s3_client = boto3.client("s3")
files_bucket_name = os.environ["FILES_BUCKET"]
dynamodb_client = boto3.resource("dynamodb")
files_table = dynamodb_client.Table(os.environ["FILES_TABLE"])
users_table = dynamodb_client.Table(os.environ["USERS_TABLE"])
sns_client = boto3.client("sns")
file_deleted_topic = os.environ["FILE_DELETED_TOPIC"]


def delete_file(event, context):
    fileName = event["queryStringParameters"].get("fileName")
    owner = event["queryStringParameters"].get("owner")
    if fileName is None or owner is None:
        return bed_request("Required parameters missing")

    file_to_delete = files_table.get_item(
        Key={"fileName": fileName, "owner": owner}
    ).get("Item")

    if file_to_delete is None:
        return bed_request("File doesn't exist")

    try:
        delete_one_file(file_to_delete, fileName, owner)
    except Exception as e:
        return server_error("Service unvailable")

    try:
        sns_client.publish(
            TopicArn=file_deleted_topic,
            Message=json.dumps(
                {
                    "event": "delete",
                    "subject": "File Successfully Deleted",
                    "content": f"{fileName} has been deleted by {owner}.",
                    "receivers": file_to_delete["haveAccess"],
                }
            ),
        )
    except Exception as e:
        print(f"[ERROR]-Delete: {e}")

    return successfull({"fileName": fileName})


def delete_one_file(file_to_delete, file_name, owner):
    users = file_to_delete["haveAccess"]
    updated_users = delete_file_in_users(owner, users, file_name)
    file_meta_data = delete_file_metadata(owner, file_name, updated_users)
    delete_from_persistent_storage(owner, file_name, updated_users, file_meta_data)


def delete_file_in_users(owner, users, file_name):
    updated_users = []

    try:
        for username in users:
            user = users_table.get_item(Key={"username": username}).get("Item")

            albums = {}
            for key in user["albums"]:
                albums[key] = []
                for userfileName in user["albums"][key]:
                    if userfileName != owner + "," + file_name:
                        albums[key].append(userfileName)

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
        raise Exception("File delete not sucessfull")
    return updated_users


def rollback_updated_users(updated_users, file_name):
    try:
        for user in updated_users:
            users_table.put_item(Item=user)
    except Exception:
        for user in updated_users:
            print(f"[ERROR]-DeleteRollback: {user['username']} {file_name} ")
        raise Exception("File delete not sucessfull")


def delete_file_metadata(owner, file_name, updated_users):
    try:
        file_meta_data = files_table.get_item(
            Key={"fileName": file_name, "owner": owner}
        )
        files_table.delete_item(Key={"fileName": file_name, "owner": owner})
    except Exception as e:
        print(f"[ERROR]-Delete: {e}")
        rollback_updated_users(updated_users, file_name)
        raise Exception("File delete not sucessfull")
    return file_meta_data


def delete_from_persistent_storage(owner, file_name, updated_users, file_meta_data):
    try:
        s3_client.delete_object(
            Bucket=files_bucket_name,
            Key=f"{owner}/{file_name}",
        ).get("DeleteMarker", False)
    except Exception as e:
        print(f"[ERROR]-Delete: {e}")
        rollback_updated_users(updated_users, file_name)
        rollback_deleted_file_meta_data(file_meta_data)
        raise Exception("File delete not sucessfull")


def rollback_deleted_file_meta_data(file_meta_data):
    files_table.put_item(Item=file_meta_data)


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
