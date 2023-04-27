import json
import boto3

client = boto3.resource('dynamodb')
user_table = client.Table('User')

def change_avatar_lambda(event, context):
    
    path_parameters = event.get('pathParameters')
    new_avatar = event.get('avatar')
    
    if path_parameters is None or path_parameters.get('username') is None or new_avatar is None:
        return bed_request("Missing required username parameter")
    
    username = path_parameters['username']
    
    response = user_table.update_item(
        Key={"username": username},
        UpdateExpression="set #avatar = :a",
        ExpressionAttributeNames={
            "#avatar": "avatar",
        },
        ExpressionAttributeValues={
            ":a": new_avatar,
        },
        ReturnValues="UPDATED_NEW",
    )

    print(response)
                
    return successfull_login()

def bed_request(message):
    return {
        "statusCode": 400,
        "body": json.dumps({
            "message": message
        }),
        }

def successfull_login(user):
    return {
        "statusCode": 200,
        "body": json.dumps(user),
    }