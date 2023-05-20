import json
import boto3
import os

dynamodb_client = boto3.resource("dynamodb")
files_table = dynamodb_client.Table(os.environ["FILES_TABLE"])


def update_file(event, context):
    fileName = event["queryStringParameters"].get("fileName")
    owner = event["queryStringParameters"].get("owner")
    if fileName is None or owner is None:
        return bed_request("Required parameters missing")

    updates = get_attributes_for_update(event)
    return successfull_update(update_file_dynamodb(updates, fileName, owner))


def get_attributes_for_update(event):
    body = json.loads(event.get("body", {}))
    return dict(body)


def update_file_dynamodb(updates, fileName, owner):
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
