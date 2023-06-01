import boto3
import json
import os

sns_client = boto3.client("sns")
dynamodb_client = boto3.resource("dynamodb")
users_table = dynamodb_client.Table(os.environ["USERS_TABLE"])
files_table = dynamodb_client.Table(os.environ["FILES_TABLE"])
invite_accepted_topic = os.environ["INVITE_ACCEPTED_TOPIC"]


def give_access_to_family_member(event, context):
    inviter = users_table.get_item(Key={"username": event["inviter"]})["Item"]

    family_member = users_table.get_item(Key={"username": event["person_invited"]})[
        "Item"
    ]

    for album_name_to_share in inviter["albums"]:
        for file_name_to_share in inviter["albums"][album_name_to_share]:
            if file_name_to_share.split(",")[0] == inviter["username"]:
                family_member["albums"]["Main Album"].append(file_name_to_share)
                update_file(
                    file_name_to_share.split(",")[1],
                    inviter["username"],
                    family_member,
                )

    return {"status": 200, "message": "ok"}


def update_file(file_name_to_share, owner_username, share_with_username):
    file_to_share = files_table.get_item(
        Key={"fileName": file_name_to_share, "owner": owner_username}
    )["Item"]
    file_to_share["haveAccess"].append(share_with_username)
    files_table.put_item(Item=file_to_share)
