import sys
import boto3
import mypy_boto3_dynamodb as dynamodb
import argparse
from config_repo import ConfigRepo


def parse_cmd_line():
    parser = argparse.ArgumentParser(
        description='Discount watch',
        epilog='Watches marketplace pages and waits for discounts')

    parser.add_argument('cmd',
                        choices=['run', 'save', 'dump'])
    parser.add_argument('-k', '--probe-key', required=True,
                        help='Name of the config key containing the probe spec')
    parser.add_argument('-f', '--probe-file',
                        help='Path to the probe spec file')
    args = parser.parse_args()
    if args.cmd == 'save':
        if args.probe_key is None:
            raise Exception('save needs --probe-file')
    return args


def get_db() -> dynamodb.ServiceResource:
    # db = boto3.resource('dynamodb',aws_access_key_id='yyyy', aws_secret_access_key='xxxx', region_name='***')
    db = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
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
            print(f'Config key {config_key} does not exist')
    else:
        print("Config table doesn't exist.s")




def main():
    args = parse_cmd_line()
    if args.cmd == 'save':
        save_probe_spec(get_db(), args.probe_file, args.probe_key)
    elif args.cmd == 'dump':
        dump_probe_spec(get_db(), args.probe_key)


if __name__ == '__main__':
    main()
