from pprint import pprint
import boto3
import mypy_boto3_lambda as aws_lambda

import aws


def delete_lambda(aws_region: str, base_name: str) -> None:
    lambda_client: aws_lambda.LambdaClient = boto3.client('lambda', region_name=aws_region)
    function_name = base_name
    f = None
    try:
        f = lambda_client.get_function(FunctionName=function_name)
    except:
        pass
    if f is not None:
        lambda_client.delete_function(FunctionName=function_name)


def deploy_lambda(zip_file: str, aws_region: str, base_name: str) -> None:
    lambda_client: aws_lambda.LambdaClient = boto3.client('lambda', region_name=aws_region)
    function_name = base_name
    lambda_client.create_function(
        FunctionName=function_name,
        Runtime='python3.12',
        Role=f'arn:aws:iam::{aws.account_id()}:role/{base_name}-role',  # tmp
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


def deploy_everything(zip_file: str, aws_region: str, base_name: str) -> None:
    delete_lambda(aws_region=aws_region, base_name=base_name)
    deploy_lambda(zip_file=zip_file, aws_region=aws_region, base_name=base_name)


def __file_contents(path: str):
    with open(path, 'rb') as file_data:
        bytes_content = file_data.read()
    return bytes_content
