import boto3

__the_aws_account_id = None


def account_id() -> str:
    global __the_aws_account_id
    if __the_aws_account_id is None:
        client = boto3.client("sts")
        __the_aws_account_id = client.get_caller_identity()["Account"]
    return __the_aws_account_id
