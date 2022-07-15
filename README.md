# Mock EC2 instance metadata endpoint on local systems for development purposes


`mock-instance-profile` provides a way to run [ec2 instance profile](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_switch-role-ec2_instance-profiles.html) on local linux or mac to simulate running on an ec2 instance. This provides a native capability to work with AWS SDKs

Read the blog post for a detailed walkthrough: [aws instance profile for local development](https://medium.com/@slimm609/aws-instance-profile-for-local-development-f144b0a7b8b9)

# Installation

Follow the installation guide for [amazon-ec2-metadata-mock](https://github.com/aws/amazon-ec2-metadata-mock) to install ec2-metadata-mock before using mock-instance-profile.

ensure you have python3 installed then install the python dependencies with pip3.

```bash
$ pip3 install -r requirements.txt
```

# local metadata mock

To mock metadata you must have some credentials on your system that boto3 can read via the [default credential chain](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html#cli-configure-quickstart-precedence).

run `mock-instance-profile` with the IAM role that you would like to assume credentials for.

```bash
$ ./mock-instance-profile arn:aws:iam::55555555555:role/my-test-role
Password:

Using configuration from file:  /Users/test-user/.aws/mock_config.json
2022/07/15 07:42:16 Initiating ec2-metadata-mock for all mocks on port 80

Flags:
config-file: /Users/test-user/.aws/mock_config.json
hostname: 169.254.169.254
port: 80

```
