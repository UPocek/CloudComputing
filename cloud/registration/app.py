import boto3
import random
import os

client = boto3.resource("dynamodb")
user_table = client.Table(os.environ["USERS_TABLE"])


def registration_lambda(event, context):
    user_attributes = event["request"]["userAttributes"]

    newUser = {}
    for key in user_attributes:
        if key in [
            "name",
            "custom:surname",
            "custom:birthday",
            "preferred_username",
            "email",
        ]:
            newUser[key.replace("custom:", "")] = user_attributes[key]

    newUser["avatar"] = get_random_avatar(newUser)
    newUser["username"] = newUser["preferred_username"]
    newUser["albums"] = {}
    del newUser["preferred_username"]
    user_table.put_item(Item=newUser)
    return event


def get_random_avatar(user):
    if user["name"][-1].lower() == "a":
        letter = "f"
    else:
        letter = random.choice(["m", "f"])
    return letter + str(random.randint(0, 7))
