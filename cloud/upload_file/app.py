import json
import boto3
import base64

dynamodb_client = boto3.resource("dynamodb")
files_table = dynamodb_client.Table("FilesMetadata")
s3_client = boto3.client("s3")
bucket_name = "cloudcomputingfiles"


def upload_file_lambda(event, context):
    body = event.get("body")

    if body is None:
        return bed_request("Missing required upload parameters")

    body = json.loads(body)

    fileContent = body.get("fileContent")
    fileName = body.get("fileName")
    fileType = body.get("fileType")
    fileSize = body.get("fileSize")
    fileCreated = body.get("fileCreated")
    fileLastModefied = body.get("fileLastModefied")
    description = body.get("description")
    tags = body.get("tags")
    owner = body.get("owner")
    haveAccsess = body.get("haveAccsess")

    if fileContent is None:
        return bed_request("Missing required upload parameters")

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
        }
    )
    s3_client.put_object(
        Bucket=bucket_name,
        Key=f"{owner}/{fileName}",
        Body=base64.b64decode(fileContent),
    )

    return successfull_upload(body)


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
