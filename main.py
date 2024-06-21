from pprint import pprint
import boto3
import mypy_boto3_dynamodb as dynamodb
import argparse
import os

from config_repo import ConfigRepo
from price_checker import run_price_check
import change_reporter
import aws_deploy


def check_required_args(args) -> None :
    req_args = {
        'run': ['probe-key'],
        'save': ['probe-key', 'probe-file'],
        'dump': ['probe-key'],
        'aws-deploy': ['aws-base-name']
    }
    cmd = args.cmd
    if cmd in req_args:
        for req_arg in req_args[cmd]:
            req_arg_field = req_arg.replace('-', '_')
            if getattr(args, req_arg_field) is None:
                raise Exception(f'{cmd} requires --{req_arg}')


def parse_cmd_line():
    parser = argparse.ArgumentParser(
        description='Watches marketplace pages and waits for discounts')

    parser.add_argument('cmd',
                        choices=['run', 'save', 'dump', 'aws-deploy'])
    parser.add_argument('-k', '--probe-key',
                        help='Name of the config key containing the probe spec')
    parser.add_argument('-f', '--probe-file',
                        help='Path to the probe spec file')
    parser.add_argument('-n', '--aws-base-name', default='sackkarre',
                        help='Base name for naming objects in AWS when deploying')
    parser.add_argument('-r', '--aws-region', default='us-east-1',
                        help='AWS region')
    args = parser.parse_args()
    check_required_args(args)
    return args


def get_db(region: str) -> dynamodb.ServiceResource:
    db = boto3.resource('dynamodb', region_name=region)
    # db = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
    return db


def save_probe_spec(db: dynamodb.ServiceResource, probe_file: str, config_key: str) -> None:
    with open(probe_file, 'r') as file:
        probe_str = file.read()
    cr = ConfigRepo(db=db)
    cr.ensure_schema()
    cr.put_value(key=config_key, value=probe_str)


def dump_probe_spec(db: dynamodb.ServiceResource, config_key: str) -> None:
    cr = ConfigRepo(db=db)
    if cr.schema_exists():
        s = cr.find_value(key=config_key)
        if s is not None:
            print(s)
        else:
            print(f'Config key {config_key} not found')
    else:
        print("Config table doesn't exist")


def deploy_to_aws(aws_region: str, base_name: str) -> None:
    zip_file = '.build/sackkarre.zip'
    if not os.path.isfile(zip_file):
        raise Exception(f'AWS lambda zip file {zip_file} not found. Run make lambda-build.')
    aws_deploy.deploy_everything(zip_file, aws_region, base_name)


def aws_lambda(event, context):
    print(f'Hello AWS.')
    pprint(event)
    pprint(context)


def main():
    args = parse_cmd_line()
    if args.cmd == 'save':
        save_probe_spec(get_db(args.aws_region), args.probe_file, args.probe_key)
    elif args.cmd == 'dump':
        dump_probe_spec(get_db(args.aws_region), args.probe_key)
    elif args.cmd == 'run':
        sns_reporter = change_reporter.AwsSnsChangeReported(
            topic_name=args.aws_base_name,
            aws_region=args.aws_region)
        stdout_reporter = change_reporter.StdoutChangeReporter()
        reporter = change_reporter.MulticastReporter([sns_reporter, stdout_reporter])
        run_price_check(get_db(args.aws_region), args.probe_key, reporter)
    elif args.cmd == 'aws-deploy':
        deploy_to_aws(args.aws_region, args.aws_base_name)


if __name__ == '__main__':
    main()
