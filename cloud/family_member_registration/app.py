import boto3
import json
import os
import random

dynamodb_client = boto3.resource("dynamodb")
user_table = dynamodb_client.Table(os.environ["USERS_TABLE"])
invitations_table = dynamodb_client.Table(os.environ["INVITATIONS_TABLE"])
cognito_client = boto3.client("cognito-idp")
users_user_pool = os.environ["USERS_USER_POOL"]


def family_member_registration(event, context):
    body = json.loads(event["body"])

    if (
        body is None
        or body.get("username") is None
        or body.get("email") is None
        or body.get("custom:surname") is None
        or body.get("custom:birthday") is None
        or body.get("preferred_username") is None
        or body.get("name") is None
        or body.get("inviter") is None
    ):
        return {"status": False}

    if not person_is_invited(body["email"], body["inviter"]):
        return {"status": False}

    try:
        cognito_client.admin_create_user(
            UserPoolId=users_user_pool,
            Username=body["username"],
            UserAttributes=[
                {"Name": "name", "Value": body["name"]},
                {"Name": "custom:surname", "Value": body["custom:surname"]},
                {"Name": "custom:birthday", "Value": body["custom:birthday"]},
                {
                    "Name": "preferred_username",
                    "Value": body["preferred_username"].replace(",", ""),
                },
                {"Name": "email", "Value": body["email"]},
            ],
        )
    except Exception:
        return {"status": False}

    newUser = {}
    for key in body:
        if key in [
            "name",
            "custom:surname",
            "custom:birthday",
            "preferred_username",
            "email",
        ]:
            newUser[key.replace("custom:", "")] = body[key]

    newUser["avatar"] = get_random_avatar(newUser)
    newUser["username"] = newUser["preferred_username"].replace(",", "")
    newUser["albums"] = {"Main Album": []}
    del newUser["preferred_username"]
    user_table.put_item(Item=newUser)
    return {
        "status": True,
        "inviter": body["inviter"],
        "person_invited": newUser["username"],
    }


def person_is_invited(person_invited, inviter):
    return (
        invitations_table.get_item(Key={"id": f"{person_invited},{inviter}"}).get(
            "Item"
        )
        is not None
    )


def get_random_avatar(user):
    if user["name"][-1].lower() == "a":
        letter = "f"
    else:
        letter = random.choice(["m", "f"])
    return letter + str(random.randint(0, 7))


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


def successfull(user):
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
        },
        "body": json.dumps(user),
    }
