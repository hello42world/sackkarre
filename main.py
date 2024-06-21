import sys
from config_repo import ConfigRepo


def main():
    if len(sys.argv) == 0:
        raise Exception('app <config_key_name> - key of the config that contains probes yaml')
    probes_key = sys.argv[1]

    # db = boto3.resource('dynamodb',aws_access_key_id='yyyy', aws_secret_access_key='xxxx', region_name='***')
    # db = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
    pass


if __name__ == '__main__':
    main()
