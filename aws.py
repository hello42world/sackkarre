from pprint import pprint

import boto3
import mypy_boto3_lambda as aws_lambda


def deploy_lambda(zip_file: str, region: str) -> None:
    lambda_client: aws_lambda.LambdaClient = boto3.client('lambda',  region_name=region)
    function_name = 'sackkarre-1'
    lambda_client.create_function(
        FunctionName=function_name,
        Runtime='python3.12',
        Role=f'arn:aws:iam::{__aws_account_id()}:role/sackkarre-role-1',  # tmp
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


__the_aws_account_id = None


def __aws_account_id() -> str:
    global __the_aws_account_id
    if __the_aws_account_id is None:
        client = boto3.client("sts")
        __the_aws_account_id = client.get_caller_identity()["Account"]
    return __the_aws_account_id
