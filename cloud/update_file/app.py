import json
import boto3
import os

dynamodb_client = boto3.resource("dynamodb")
files_table = dynamodb_client.Table(os.environ["FILES_TABLE"])
sns_client = boto3.client("sns")
file_updated_topic = os.environ["FILE_UPDATED_TOPIC"]


def update_file(event, context):
    fileName = event["queryStringParameters"].get("fileName")
    owner = event["queryStringParameters"].get("owner")
    if fileName is None or owner is None:
        return bed_request("Required parameters missing")

    updates = get_attributes_for_update(event)

    file_to_update = files_table.get_item(
        Key={"fileName": fileName, "owner": owner}
    ).get("Item")

    if file_to_update is None or file_to_update.get("haveAccess") is None:
        return bed_request("File does not exist")

    new_metadata = update_file_metadata(updates, fileName, owner)
    if new_metadata:
        try:
            sns_client.publish(
                TopicArn=file_updated_topic,
                Message=json.dumps(
                    {
                        "event": "update",
                        "subject": "File Successfully Updated",
                        "content": f"{fileName} has been updated by {owner}.",
                        "receivers": file_to_update["haveAccess"],
                    }
                ),
            )
        except Exception as e:
            print(f"[ERROR]-Update: {e}")
    else:
        return server_error("Service unavilable")

    return successfull_update(new_metadata)


def get_attributes_for_update(event):
    body = json.loads(event.get("body"))
    if body.get("tags"):
        body["tags"] = body["tags"].split(",")
        if body["tags"] == [""]:
            body["tags"] = []
    return dict(body)


def update_file_metadata(updates, fileName, owner):
    update_expression = "SET " + ", ".join(
        [f"{key} = :{key}" for key in updates.keys()]
    )
    expression_attribute_values = {f":{key}": updates[key] for key in updates.keys()}
    return files_table.update_item(
        Key={"fileName": fileName, "owner": owner},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values,
        ReturnValues="UPDATED_NEW",
    ).get("Attributes")


def server_error(message):
    return {
        "statusCode": 503,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "PUT",
        },
        "body": json.dumps({"message": message}),
    }


def bed_request(message):
    return {
        "statusCode": 400,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "PUT",
        },
        "body": json.dumps({"message": message}),
    }


def successfull_update(file):
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "PUT",
        },
        "body": json.dumps(file),
    }
