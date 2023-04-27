import json
import boto3
import random


def registration_lambda(event, context):
    client = boto3.resource("dynamodb")
    user_table = client.Table("User")

    
    newUser = event.get("newUser")
    if newUser is None:
        return bed_request("Required parameters missing")
    if(set(newUser.keys()) != set(['name', 'surname', 'birthday', 'username', 'email', 'password'])):
        return bed_request("Required parameters missing")
    
    username = newUser['username']

    user = user_table.get_item(Key={"username": username})
    if user.get("Item") is not None:
        return bed_request("Username already exists!")

    newUser['avatar'] = get_random_avatar(newUser)
    _ = user_table.put_item(Item=newUser)
    return successfull_registration(newUser)


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

def get_random_avatar(user):
    if (user['name'][-1].lower() == 'a'):
        letter = 'f'
    else:
        letter = random.choice(['m', 'f'])
    return letter + str(random.randint(0,7))
