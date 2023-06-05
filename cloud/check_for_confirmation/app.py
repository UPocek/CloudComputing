import boto3
import os

dynamodb_client = boto3.resource("dynamodb")
invitations_table = dynamodb_client.Table(os.environ["INVITATIONS_TABLE"])


def check_for_confirmation(event, context):
    inviter = event["inviter"]
    person_invited = event["person_invited"]

    invitation = invitations_table.get_item(
        Key={"id": f"{person_invited},{inviter}"}
    ).get("Item")

    if invitation is None or invitation["status"] == "pending":
        raise Exception("Not yet confirmed")

    print(invitation)

    return {
        "status": invitation["status"] == "accept",
        "inviter": inviter,
        "person_invited": person_invited,
    }
