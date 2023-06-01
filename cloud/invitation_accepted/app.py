import boto3
import json
import os

sns_client = boto3.client("sns")
invite_accepted_topic = os.environ["INVITE_ACCEPTED_TOPIC"]


def invitation_accepted(event, context):
    inviter = event["inviter"]
    person_invited = event["person_invited"]
    sns_client.publish(
        TopicArn=invite_accepted_topic,
        Message=json.dumps(
            {
                "subject": f"{person_invited} Accepted Invitation",
                "content": f"Hey, new family member {person_invited} has accepted your invitation 🎉.\n To grant family member access to your Lightning Gallery files click on GIVE ACCESS.\n If you don't want to grant access click on DON'T GIVE ACCESS",
                "receivers": inviter,
            }
        ),
    )

    return event
