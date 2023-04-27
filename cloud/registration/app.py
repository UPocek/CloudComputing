import json
import boto3

# import requests


def registration_lambda(event, context):
    client = boto3.resource("dynamodb")
    user_table = client.Table("User")

    
    username = event.get("newUser").get("username")

    user = user_table.get_item(Key={"username": username})
    if user.get("Item") is not None:
        return bed_request("Username already exists!")

    _ = user_table.put_item(Item=event["newUser"])
    return successfull_registration(event.get("newUser"))


def bed_request(message):
    return {
        "statusCode": 400,
        "body": json.dumps({"message": message}),
    }


def successfull_registration(user):
    del user["password"]
    return {
        "statusCode": 200,
        "body": json.dumps(user),
    }
