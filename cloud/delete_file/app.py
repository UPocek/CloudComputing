import json
import boto3
import os

s3_client = boto3.client("s3")
files_bucket_name = os.environ["FILES_BUCKET"]
dynamodb_client = boto3.resource("dynamodb")
files_table = dynamodb_client.Table(os.environ["FILES_TABLE"])
users_table = dynamodb_client.Table(os.environ["USERS_TABLE"])


def delete_file(event, context):
    fileName = event["queryStringParameters"].get("fileName")
    owner = event["queryStringParameters"].get("owner")
    if fileName is None or owner is None:
        return bed_request("Required parameters missing")
    is_deleted = delete_one_file(fileName, owner)

    return successfull({"fileName": fileName, "deleted": is_deleted})


def delete_one_file(fileName, owner):
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
    return s3_client.delete_object(
        Bucket=files_bucket_name,
        Key=f"{owner}/{fileName}",
    ).get("DeleteMarker", False)


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
