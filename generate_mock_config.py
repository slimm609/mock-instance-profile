#!/usr/bin/env python3

import boto3
import json
import random
import argparse
import sys
import datetime
import secrets
import os

templateFileName = "mock_template.json"
homeDir = os.environ.get("HOME")
outputFile = os.path.join(homeDir, ".aws", "mock_config.json")


def renderMockTemplate(roleArn):
    """
    creates tag pointing to ref
    :param roleArn: name of the AWS role Arn to assume
    :return: None
    """
    creds = assumeMockRole(roleArn)
    # get the role name from the roleArn so we can inject to the template
    roleName = roleArn.split("/")[1]
    accountId = roleArn.split(":")[4]
    expiration = creds["Expiration"]

    now = datetime.datetime.now()
    with open(templateFileName, "r") as f:
        template = json.load(f)

        # update the roleName and roleArn in the template
        template["metadata"]["values"]["iam-security-credentials-role"] = roleName
        template["metadata"]["paths"][
            "iam-security-credentials"
        ] = "/latest/meta-data/iam/security-credentials/{}".format(roleName)
        template["metadata"]["values"]["iam-info"]["InstanceProfileArn"] = roleArn

        # update the security credentials from the assume-role
        template["metadata"]["values"]["iam-security-credentials"][
            "AccessKeyId"
        ] = creds["AccessKeyId"]
        template["metadata"]["values"]["iam-security-credentials"][
            "SecretAccessKey"
        ] = creds["SecretAccessKey"]
        template["metadata"]["values"]["iam-security-credentials"]["Token"] = creds[
            "SessionToken"
        ]
        template["metadata"]["values"]["iam-info"]["InstanceProfileId"] = creds[
            "AccessKeyId"
        ]

        # update the LastUpdated time to now
        template["metadata"]["values"]["iam-security-credentials"][
            "LastUpdated"
        ] = now.strftime("%Y-%m-%dT%H:%M:%S%z")
        template["metadata"]["values"]["iam-info"]["LastUpdated"] = now.strftime(
            "%Y-%m-%dT%H:%M:%S+00:00"
        )

        # update the expiration time
        template["metadata"]["values"]["iam-security-credentials"][
            "Expiration"
        ] = expiration.strftime("%Y-%m-%dT%H:%M:%S+00:00")

        # update the accountId
        template["dynamic"]["values"]["instance-identity-document"][
            "accountId"
        ] = accountId

        # update the amiID
        amiId = "ami-{}".format(secrets.token_hex(9)[:-1])
        instanceId = "ami-{}".format(secrets.token_hex(9)[:-1])
        template["dynamic"]["values"]["instance-identity-document"]["imageId"] = amiId
        template["dynamic"]["values"]["instance-identity-document"][
            "instanceId"
        ] = instanceId
        template["metadata"]["values"]["ami-id"] = amiId
        template["metadata"]["values"]["instance-id"] = instanceId

        # Generate a random IP address
        randomIP = ".".join(
            map(
                str,
                (
                    [
                        10,
                        random.randint(0, 255),
                        random.randint(0, 255),
                        random.randint(0, 255),
                    ]
                ),
            )
        )
        template["dynamic"]["values"]["instance-identity-document"][
            "privateIp"
        ] = randomIP
        template["metadata"]["values"]["local-ipv4"] = randomIP
        template["metadata"]["values"]["mac-local-ipv4s"] = randomIP
        template["metadata"]["values"]["public-ipv4"] = randomIP

        # generate hostname from ip address
        octets = randomIP.split(".")
        hostname = "ec2-{}-{}-{}-{}.compute-1.amazonaws.com".format(
            octets[0], octets[1], octets[2], octets[3]
        )
        template["metadata"]["values"]["public-hostname"] = hostname
        template["metadata"]["values"]["mac-public-hostname"] = hostname
        template["metadata"]["values"]["public-hostname"] = hostname

        # generate internal hostname
        internalHostname = "ip-{}-{}-{}-{}.ec2.internal".format(
            octets[0], octets[1], octets[2], octets[3]
        )
        template["metadata"]["values"]["mac-local-hostname"] = internalHostname
        template["metadata"]["values"]["local-hostname"] = internalHostname
        template["metadata"]["values"]["hostname"] = internalHostname

        with open(outputFile, "w+") as f:
            f.write(json.dumps(template))


def assumeMockRole(roleArn):
    """
    AWS assume role credentials
    :param roleArn: name of the AWS role Arn to assume
    :return: AWS credentials
    """
    sessionName = "ec2-mock-{}".format(random.randrange(10000))
    client = boto3.client("sts")

    response = client.assume_role(
        RoleArn=roleArn,
        RoleSessionName=sessionName,
        DurationSeconds=3600,  # this can be updated to match the expected duration needed
    )

    return response["Credentials"]


# Get input from the user.
def parser(args):
    parser = argparse.ArgumentParser(description="get images")
    parser.add_argument(
        "--roleArn", "-r", dest="roleArn", help="AWS Role Arn", required=True
    )
    args = parser.parse_args(args)

    renderMockTemplate(**vars(args))


if __name__ == "__main__":
    parser(sys.argv[1:])
