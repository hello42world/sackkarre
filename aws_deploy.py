from pprint import pprint
import boto3
import mypy_boto3_lambda as aws_lambda
import mypy_boto3_iam as aws_iam
import json

import aws


def delete_lambda(aws_region: str, base_name: str) -> None:
    lambda_client: aws_lambda.LambdaClient = boto3.client('lambda', region_name=aws_region)
    function_name = base_name
    f = None
    try:
        f = lambda_client.get_function(FunctionName=function_name)
    except lambda_client.exceptions.ResourceNotFoundException:
        pass
    if f is not None:
        lambda_client.delete_function(FunctionName=function_name)


def deploy_lambda(zip_file: str, aws_region: str, base_name: str) -> None:
    lambda_client: aws_lambda.LambdaClient = boto3.client('lambda', region_name=aws_region)
    function_name = base_name
    lambda_client.create_function(
        FunctionName=function_name,
        Runtime='python3.12',
        Role=f'arn:aws:iam::{aws.account_id()}:role/{base_name}',
        Code={
            'ZipFile': __file_contents(zip_file)
        },
        Handler='main.aws_lambda',
        Description='Sackkarre watches for discounts!',
        PackageType='Zip',
        Architectures=['x86_64'],
        Publish=True,
        Timeout=60,
        Environment={
            'Variables': {
                'PROBE_KEY': 'test1'
            }
        }
    )
    waiter = lambda_client.get_waiter('function_updated')
    waiter.wait(FunctionName=function_name)
    res = lambda_client.get_function(FunctionName=function_name)
    print('===== Lambda created =====')
    pprint(res)


def delete_iam_role(base_name: str):
    iam: aws_iam.ServiceResource = boto3.resource("iam")
    try:
        iam.Role(base_name).delete()
    except iam.meta.client.exceptions.NoSuchEntityException:
        pass


def detach_iam_policy(base_name: str):
    iam: aws_iam.ServiceResource = boto3.resource("iam")
    try:
        policy_arn = f'arn:aws:iam::{aws.account_id()}:policy/{base_name}'
        iam.Role(base_name).detach_policy(PolicyArn=policy_arn)
    except iam.meta.client.exceptions.NoSuchEntityException:
        pass


def deploy_iam_role(base_name: str) -> None:
    iam: aws_iam.ServiceResource = boto3.resource("iam")
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
    role = iam.create_role(
        RoleName=base_name,
        AssumeRolePolicyDocument=json.dumps(trust_policy)
    )
    print('===== IAM role created =====')
    pprint(role)


def attach_iam_policy(base_name: str) -> None:
    iam: aws_iam.ServiceResource = boto3.resource("iam")
    role = iam.Role(base_name)
    policy_arn = f'arn:aws:iam::{aws.account_id()}:policy/{base_name}'
    role.attach_policy(PolicyArn=policy_arn)


def deploy_iam_policy(base_name: str) -> None:
    iam: aws_iam.ServiceResource = boto3.resource("iam")
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

    policy = iam.create_policy(
        PolicyName=base_name,
        Description=f'{base_name} security policy',
        PolicyDocument=json.dumps(policy_doc),
    )
    print('===== IAM policy created =====')
    pprint(policy)


def delete_iam_policy(base_name: str) -> None:
    iam: aws_iam.ServiceResource = boto3.resource("iam")
    try:
        iam.Policy(f'arn:aws:iam::{aws.account_id()}:policy/{base_name}').delete()
    except iam.meta.client.exceptions.NoSuchEntityException:
        pass


def deploy_everything(zip_file: str, aws_region: str, base_name: str) -> None:
    delete_lambda(aws_region=aws_region, base_name=base_name)
    detach_iam_policy(base_name)
    delete_iam_policy(base_name)
    delete_iam_role(base_name)

    deploy_iam_policy(base_name)
    deploy_iam_role(base_name)
    attach_iam_policy(base_name)
    deploy_lambda(zip_file=zip_file, aws_region=aws_region, base_name=base_name)


def __file_contents(path: str):
    with open(path, 'rb') as file_data:
        bytes_content = file_data.read()
    return bytes_content
