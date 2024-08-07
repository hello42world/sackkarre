import asyncio
from pprint import pprint
import boto3
import mypy_boto3_dynamodb as dynamodb
import argparse
import os
from aiohttp import ClientSession

import tabulate

import probe_io
from config_repo import ConfigRepo
from price_checker import run_price_check
import change_reporter
import aws_deploy

import probe
import probe_state_repo


def check_required_args(args) -> None:
    req_args = {
        'run-local': ['probe-list-name'],
        'set-probe-list': ['probe-list-name', 'probe-list-file'],
        'get-probe-list': ['probe-list-name'],
        'aws-deploy': ['base-name'],
        'aws-delete': ['base-name'],
        'list-probe-state': []
    }
    cmd = args.cmd
    if cmd in req_args:
        for req_arg in req_args[cmd]:
            req_arg_field = req_arg.replace('-', '_')
            if getattr(args, req_arg_field) is None:
                raise Exception(f'{cmd} requires --{req_arg}')


def parse_cmd_line():
    parser = argparse.ArgumentParser(
        description='Watches marketplace pages and waits for changes in price')

    parser.add_argument('cmd',
                        choices=['run-local', 'set-probe-list', 'get-probe-list', 'aws-deploy', 'aws-delete',
                                 'list-probe-state'],
                        help='''
run-local - Run the price checker locally (using db in the cloud) |
set-probe-list - Save probe list file to the config |
get-probe-list - Load probe list from the config |
aws-deploy - Deploy the lambda and IAM policy/role to AWS |
aws-delete - Delete the lambda and IAM policy/role from AWS (leaves the data in dynamodb & the topic) |
list-probe-state - list probes and their current state
                        ''')
    parser.add_argument('-n', '--probe-list-name', default='default_probe_list',
                        help='Name of the config value containing the probe list')
    parser.add_argument('-f', '--probe-list-file',
                        help='Path to the probe list file')
    parser.add_argument('-b', '--base-name', default='sackkarre',
                        help='Base name (prefix) for naming objects in AWS when deploying')
    parser.add_argument('-r', '--aws-region', default='us-east-1',
                        help='AWS region')
    args = parser.parse_args()
    check_required_args(args)
    return args


def get_db(region: str) -> dynamodb.ServiceResource:
    db = boto3.resource('dynamodb', region_name=region)
    # db = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
    return db


def save_probe_spec(db: dynamodb.ServiceResource, base_name: str, probe_list_file: str, config_key: str) -> None:
    with open(probe_list_file, 'r') as file:
        probe_str = file.read()
    # This will do a syntax check.
    probe_io.load_from_str(probe_str)
    cr = ConfigRepo(db=db, base_name=base_name)
    cr.ensure_schema()
    cr.put_value(key=config_key, value=probe_str)


def dump_probe_spec(db: dynamodb.ServiceResource, base_name: str, config_key: str) -> None:
    cr = ConfigRepo(db=db, base_name=base_name)
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
    ad = aws_deploy.AwsDeploy(aws_region=aws_region)
    ad.deploy_everything(zip_file, base_name)


def delete_from_aws(aws_region: str, base_name: str) -> None:
    ad = aws_deploy.AwsDeploy(aws_region=aws_region)
    ad.delete_everything(base_name)


def get_reporter(base_name: str, aws_region: str) -> change_reporter.IChangeReporter:
    sns_reporter = change_reporter.AwsSnsChangeReported(
        topic_name=base_name,
        aws_region=aws_region)
    stdout_reporter = change_reporter.StdoutChangeReporter()
    reporter = change_reporter.MulticastReporter([sns_reporter, stdout_reporter])
    return reporter


def list_price_probe_state(
        db: dynamodb.ServiceResource,
        base_name: str,
        probe_list_name: str):
    cr = ConfigRepo(db, base_name)
    probe_spec_str = cr.find_value(probe_list_name)
    if probe_spec_str is None:
        raise Exception(f'Config key {probe_list_name} not found')
    probes = probe_io.load_from_str(probe_spec_str)
    state_repo = probe_state_repo.ProbeStateRepo(db, base_name)
    headers = ['ID', 'NAME', 'VALUE', 'OLD_VALUE', 'IS_ERR', 'LAST_UPD', 'URL']
    table = []
    for probe in probes:
        row = [probe.probe_id, probe.probe_name]
        state = state_repo.find_state(probe.probe_id)
        if state is not None:
            row.extend((state.value, state.old_value, state.has_error, state.last_updated.strftime("%Y-%m-%d, %H:%M:%S")))
        else:
            row.extend(('', '', '', ''))
        row.append(probe.target_url)
        table.append(row)
    print(tabulate.tabulate(table, headers))


def aws_lambda(event, context):
    probe_list_name = os.environ['PROBE_LIST_NAME']
    aws_region = os.environ['AWS_REGION']
    base_name = context.function_name
    run_price_check(get_db(aws_region), base_name, probe_list_name, get_reporter(base_name, aws_region))


def main():
    args = parse_cmd_line()
    if args.cmd == 'set-probe-list':
        save_probe_spec(get_db(args.aws_region), args.base_name, args.probe_list_file, args.probe_list_name)
    elif args.cmd == 'get-probe-list':
        dump_probe_spec(get_db(args.aws_region), args.base_name, args.probe_list_name)
    elif args.cmd == 'run-local':
        run_price_check(
            get_db(args.aws_region),
            args.base_name,
            args.probe_list_name,
            get_reporter(args.base_name, args.aws_region))
    elif args.cmd == 'aws-deploy':
        deploy_to_aws(args.aws_region, args.base_name)
    elif args.cmd == 'aws-delete':
        delete_from_aws(args.aws_region, args.base_name)
    elif args.cmd == 'list-probe-state':
        list_price_probe_state(get_db(args.aws_region), args.base_name, args.probe_list_name)
    else:
        raise Exception(f'Unknown command - {args.cmd}')


if __name__ == '__main__':
    main()
