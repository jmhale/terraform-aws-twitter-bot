"""
Script to check and keep track of Twitter handles that get released for registration
"""
# pylint: disable=W0613

import os
import sys
import requests
import boto3
from base64 import b64decode

ACCOUNTS_CHECK_KEY = "twitter_accounts_check"
ACCOUNTS_FOUND_KEY = "twitter_accounts_found"
ACCOUNTS_CHECK_PATH = '/tmp/{}'.format(ACCOUNTS_CHECK_KEY)
ACCOUNTS_FOUND_PATH = "/tmp/{}".format(ACCOUNTS_FOUND_KEY)
S3_BUCKET = os.environ['S3_BUCKET']
S3_CLIENT = boto3.client('s3')
KMS_CLIENT = boto3.client('kms')
SLACK_WEBHOOK = KMS_CLIENT.decrypt(CiphertextBlob=b64decode(os.environ['SLACK_WEBHOOK']))['Plaintext']


def post_to_slack(user=None, message=None):
    """ posts messages to Slack incoming webhook """
    if not user:
        msg = message
    else:
        msg = "Twitter handle {} is available!".format(user)

    slack_payload = {
        "channel": "#alerts",
        "username": "twitter-bot",
        "text": msg,
        "icon_emoji": ":ghost:"
    }
    requests.post(SLACK_WEBHOOK, json=slack_payload)

def handler(event, context):
    """ main Lambda handler """
    unavailable_accounts = []
    try:
        S3_CLIENT.download_file(S3_BUCKET, ACCOUNTS_CHECK_KEY, ACCOUNTS_CHECK_PATH)
    except:
        post_to_slack(message="There was a problem downloading the account check file from S3. Ensure the file exists.")
        sys.exit(1)

    with open(ACCOUNTS_CHECK_PATH, "r") as file_in:
        with open(ACCOUNTS_FOUND_PATH, "a") as file_out:
            for line in file_in:
                user = line.strip("\n")
                request_url = "https://twitter.com/{}".format(user)
                request = requests.get(request_url)
                result = request.text.find("that page doesn’t exist!")
                if result != -1:
                    print("account {} does not exist!".format(user))
                    post_to_slack(user=user)
                    file_out.write("{}\n".format(user))
                else:
                    unavailable_accounts.append(user)
        S3_CLIENT.upload_file(ACCOUNTS_FOUND_PATH, S3_BUCKET, ACCOUNTS_FOUND_KEY)

    # Re-write still unavailable accounts back to the file for subsequent checks
    with open(ACCOUNTS_CHECK_PATH, "w") as file_out:
        for line in unavailable_accounts:
            file_out.write("{}\n".format(line))
    S3_CLIENT.upload_file(ACCOUNTS_CHECK_PATH, S3_BUCKET, ACCOUNTS_CHECK_KEY)
