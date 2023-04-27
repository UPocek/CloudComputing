import json
import boto3

def bed_request(message):
    return {
        "statusCode": 400,
        "body": json.dumps({
            "message": message
        }),
        }

successfull_login = {
        "statusCode": 200
    }

client = boto3.resource('dynamodb')
user_table = client.Table('User')

def login_lambda(event, context):
    
    username = event.get('username')
    password = event.get('password')
    
    if username is None or password is None:
        return bed_request("Missing required login parameters",)
    
    response = user_table.get_item(Key={'username':username})
    user = response.get('Item')
    
    if user is None or user['password'] != password:
        return bed_request("Invalid username or password")
        
    # JWT logic 
                
    return successfull_login
