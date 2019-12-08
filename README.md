# terraform-aws-twitter-bot

Deploys a Lambda function that watches for Twitter handles to become available

## Prerequisites
- Create a KMS key for the project to use
  - The KMS key is not included in this module, because you must encrypt your Slack webhook URL and include it as a variable here before Terraform can deploy the module.
- Create a Incoming Webhook with Slack.
  - https://slack.com/apps/A0F7XDUAZ-incoming-webhooks
- Encrypt the webhook URL with the KMS key and include it as a variable. See below.
  - `aws kms encrypt --key-id 123456-7890-abcd-efgh-98765432210 --plaintext fileb://<(echo -n 'https://hooks.slack.com/services/ABCDEFGH/IJKLMNO/123456abcdefgh') --query CiphertextBlob`

### Build python deps
The `requests` Python module is needed for this script to run. Since Lambda doesn't include `requests` natively, I've included it in this repo, but in case you need to update or re-add it, run the following command:
`cd twitter-bot && pip install requests -t .`

## Variables
| Variable Name | Type | Required |Description |
|---------------|-------------|-------------|-------------|
|`bucket_name`|`string`|Yes|The name of the S3 bucket that will store the list of accounts to check.|
|`kms_key_arn`|`string`|Yes|ARN of the KMS key used to encrypt secrets related to this module.|
|`encrypted_slack_webhook`|`string`|Yes|KMS encrypted Slack webhook URL.|
|`env`|`string`|No|Name of the environment. Used to differentiate multiple deployments. Defaults to `prod`.|


## Usage

```
module "terraform-aws-twitter-bot" {
  source                  = "git@github.com:jmhale/terraform-aws-twitter-bot.git"
  kms_key_arn             = "arn:aws:kms:us-east-1:0123456789:key/123456-7890-abcd-efgh-98765432210"
  bucket_name             = "twitter-bot"
  encrypted_slack_webhook = "AQICAHgjMB0yYOA53.....Y7VJgRtp08thzydtjt75arTljI="
  env                     = "prod"
}

```

Once the module is deployed, you'll need to upload a file named `twitter_accounts_check` to the S3 bucket that is created.

This will must contain the list of account handles to check. One account per line.

## Outputs
None


---
Copyright © 2019, James Hale
