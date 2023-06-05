import boto3
import json
import os

sns_client = boto3.client("sns")
invite_accepted_topic = os.environ["INVITE_ACCEPTED_TOPIC"]
base_url = os.environ["BASE_URL"]


def invitation_accepted(event, context):
    inviter = event["inviter"]
    person_invited = event["person_invited"]
    sns_client.publish(
        TopicArn=invite_accepted_topic,
        Message=json.dumps(
            {
                "subject": f"{person_invited} Accepted Invitation",
                "content": f"Hey, new family member {person_invited} has accepted your invitation 🎉.\n\n To grant family member access to your Lightning Gallery files click on {base_url}/resolve-invite?action=accept&invite={person_invited},{inviter} .\n\n If you don't want to grant access click on {base_url}/resolve-invite?action=deny&invite={person_invited},{inviter} ",
                "receiver": inviter,
            }
        ),
    )

    return event
