import json
import boto3
import base64
import os

dynamodb_client = boto3.resource("dynamodb")
files_table = dynamodb_client.Table(os.environ["FILES_TABLE"])
users_table = dynamodb_client.Table(os.environ["USERS_TABLE"])
cognito_client = boto3.client("cognito-idp")
s3_client = boto3.client("s3")
bucket_name = os.environ["FILES_BUCKET"]
sns_client = boto3.client("sns")
file_uploaded_topic = os.environ["FILE_UPLOADED_TOPIC"]


def upload_file_lambda(event, context):
    body = json.loads(event["body"])

    if body.get("fileContent") is None:
        return bed_request("Missing required upload parameters")

    albumName = event.get("queryStringParameters", {}).get("albumName")

    jwt_token = get_jwt_from_header(event)
    user = get_user_from_cognito(jwt_token)
    user = users_table.get_item(Key={"username": user["preferred_username"]})["Item"]

    fileContent = body.get("fileContent")
    fileName = body.get("fileName").replace(",", "")
    fileType = body.get("fileType")
    fileSize = body.get("fileSize")
    fileCreated = body.get("fileCreated")
    fileLastModefied = body.get("fileLastModefied")
    description = body.get("description")
    tags = body.get("tags")
    owner = body.get("owner")
    haveAccsess = body.get("haveAccsess")

    album_to_add_file = (
        os.environ["MAIN_ALBUM_NAME"] if albumName is None else albumName
    )
    user["albums"][album_to_add_file].append(f"{owner},{fileName}")
    users_table.put_item(Item=user)

    fileContent = fileContent.split(",")[1]

    files_table.put_item(
        Item={
            "fileName": fileName,
            "fileType": fileType,
            "fileSize": fileSize,
            "fileCreated": fileCreated,
            "fileLastModefied": fileLastModefied,
            "description": description,
            "tags": tags,
            "owner": owner,
            "haveAccess": haveAccsess,
            "albums": [],
        }
    )
    s3_client.put_object(
        Bucket=bucket_name,
        Key=f"{owner}/{fileName}",
        Body=base64.b64decode(fileContent),
    )

    sns_client.publish(
        TopicArn=file_uploaded_topic,
        Message=json.dumps(
            {
                "event": "upload",
                "subject": "File Successfully Uploaded",
                "content": f"{fileName} has been uploaded.",
                "receivers": haveAccsess,
            }
        ),
    )

    return successfull_upload(body)


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
