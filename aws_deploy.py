from pprint import pprint
import boto3
import botocore.client
import mypy_boto3_lambda as aws_lambda
import mypy_boto3_iam as aws_iam
import mypy_boto3_sns as sns
import json

import aws


class AwsDeploy:
    def __init__(self, aws_region: str):
        self.lambda_client: aws_lambda.LambdaClient = boto3.client(
            'lambda',
            region_name=aws_region)
        self.aws_region = aws_region
        self.iam_client: aws_iam.ServiceResource = boto3.resource("iam")

    def delete_lambda(self, base_name: str) -> None:
        function_name = base_name
        f = None
        try:
            f = self.lambda_client.get_function(FunctionName=function_name)
        except self.lambda_client.exceptions.ResourceNotFoundException:
            pass
        if f is not None:
            self.lambda_client.delete_function(FunctionName=function_name)

    def deploy_lambda(self, zip_file: str, base_name: str) -> None:
        function_name = base_name
        # Need a lot of timeout.
        lambda_client: aws_lambda.LambdaClient = boto3.client(
            'lambda',
            region_name=self.aws_region,
            config=botocore.client.Config(read_timeout=600, connect_timeout=600))
        lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.12',
            Role=f'arn:aws:iam::{aws.account_id()}:role/{base_name}',
            Code={
                'ZipFile': self.__file_contents(zip_file)
            },
            Handler='main.aws_lambda',
            Description='Sackkarre watches for discounts!',
            PackageType='Zip',
            Architectures=['x86_64'],
            Publish=True,
            Timeout=60,
            Environment={
                'Variables': {
                    'PROBE_LIST_NAME': 'default_probe_list',
                }
            }
        )
        waiter = self.lambda_client.get_waiter('function_updated')
        waiter.wait(FunctionName=function_name)
        res = self.lambda_client.get_function(FunctionName=function_name)
        print('===== Lambda created =====')
        pprint(res)

    def __file_contents(self, path: str):
        with open(path, 'rb') as file_data:
            bytes_content = file_data.read()
        return bytes_content

    def ensure_sns_topic(self, base_name: str):
        the_sns: sns.ServiceResource = boto3.resource('sns', region_name=self.aws_region)
        topic = the_sns.create_topic(Name=base_name)
        print('===== SNS topic created =====')
        pprint(topic)

    def delete_iam_role(self, base_name: str):
        try:
            self.iam_client.Role(base_name).delete()
        except self.iam_client.meta.client.exceptions.NoSuchEntityException:
            pass

    def detach_iam_policy(self, base_name: str):
        try:
            policy_arn = f'arn:aws:iam::{aws.account_id()}:policy/{base_name}'
            self.iam_client.Role(base_name).detach_policy(PolicyArn=policy_arn)
        except self.iam_client.meta.client.exceptions.NoSuchEntityException:
            pass

    def deploy_iam_role(self, base_name: str) -> None:
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "sts:AssumeRole"
                    ],
                    "Principal": {
                        "Service": [
                            "lambda.amazonaws.com"
                        ]
                    }
                }
            ]
        }
        role = self.iam_client.create_role(
            RoleName=base_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy)
        )
        print('===== IAM role created =====')
        pprint(role)

    def attach_iam_policy(self, base_name: str) -> None:
        role = self.iam_client.Role(base_name)
        policy_arn = f'arn:aws:iam::{aws.account_id()}:policy/{base_name}'
        role.attach_policy(PolicyArn=policy_arn)
        print('===== IAM policy attached =====')

    def deploy_iam_policy(self, base_name: str) -> None:
        policy_doc = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "dynamodb:BatchGetItem",
                        "dynamodb:GetItem",
                        "dynamodb:Query",
                        "dynamodb:Scan",
                        "dynamodb:BatchWriteItem",
                        "dynamodb:PutItem",
                        "dynamodb:UpdateItem",
                        "dynamodb:CreateTable",
                        "dynamodb:DescribeTable"
                    ],
                    "Resource": [
                        f"arn:aws:dynamodb:us-east-1:{aws.account_id()}:table/{base_name}_probe_state",
                        f"arn:aws:dynamodb:us-east-1:{aws.account_id()}:table/{base_name}_config"
                    ]
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogStream",
                        "logs:PutLogEvents"
                    ],
                    "Resource": f"arn:aws:logs:us-east-1:{aws.account_id()}:*"
                },
                {
                    "Effect": "Allow",
                    "Action": "logs:CreateLogGroup",
                    "Resource": "*"
                },
                {
                    "Effect": "Allow",
                    "Resource": f"arn:aws:sns:us-east-1:{aws.account_id()}:{base_name}",
                    "Action": [
                        "sns:Publish",
                        "sns:CreateTopic"
                    ]
                }
            ]
        }

        policy = self.iam_client.create_policy(
            PolicyName=base_name,
            Description=f'{base_name} security policy',
            PolicyDocument=json.dumps(policy_doc),
        )
        print('===== IAM policy created =====')
        pprint(policy)

    def delete_iam_policy(self, base_name: str) -> None:
        try:
            policy = self.iam_client.Policy(f'arn:aws:iam::{aws.account_id()}:policy/{base_name}')
            for pv in policy.versions.all():
                if not pv.is_default_version:
                    pv.delete()
            policy.delete()
        except self.iam_client.meta.client.exceptions.NoSuchEntityException:
            pass

    def deploy_everything(self, zip_file: str, base_name: str) -> None:
        self.deploy_iam_policy(base_name=base_name)
        self.deploy_iam_role(base_name=base_name)
        self.attach_iam_policy(base_name=base_name)
        self.ensure_sns_topic(base_name=base_name)
        self.deploy_lambda(zip_file=zip_file, base_name=base_name)

    def delete_everything(self, base_name: str):
        self.delete_lambda(base_name=base_name)
        self.detach_iam_policy(base_name=base_name)
        self.delete_iam_policy(base_name=base_name)
        self.delete_iam_role(base_name=base_name)
