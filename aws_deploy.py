from pprint import pprint
import boto3
import mypy_boto3_lambda as aws_lambda

import aws


def deploy_lambda(zip_file: str, region: str) -> None:
    lambda_client: aws_lambda.LambdaClient = boto3.client('lambda',  region_name=region)
    function_name = 'sackkarre-1'
    lambda_client.create_function(
        FunctionName=function_name,
        Runtime='python3.12',
        Role=f'arn:aws:iam::{aws.account_id()}:role/sackkarre-role-1',  # tmp
        Code={
            'ZipFile': __file_contents(zip_file)
        },
        Handler='main.aws_lambda',
        Description='Sackkarre watches for discounts!',
        PackageType='Zip',
        Architectures=['x86_64'],
        Publish=True,
    )
    waiter = lambda_client.get_waiter('function_updated')
    waiter.wait(FunctionName=function_name)
    res = lambda_client.get_function(FunctionName=function_name)

    pprint(res)


def __file_contents(path: str):
    with open(path, 'rb') as file_data:
        bytes_content = file_data.read()
    return bytes_content



