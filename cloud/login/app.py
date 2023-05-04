import json
import boto3

client = boto3.resource("dynamodb")
user_table = client.Table("User")


def login_lambda(event, context):
    body = event.get("body")

    if body is None:
        return bed_request("Missing required login parameters")

    body = json.loads(body)

    username = body.get("username")
    password = body.get("password")

    if username is None or password is None:
        return bed_request("Missing required login parameters")

    response = user_table.get_item(Key={"username": username})
    user = response.get("Item")

    if user is None or user["password"] != password:
        return bed_request("Invalid username or password")

    # JWT logic

    return successfull_login(user)


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


def successfull_login(user):
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
        },
        "body": json.dumps(user),
    }
