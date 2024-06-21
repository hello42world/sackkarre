from probe_state import ProbeState
import mypy_boto3_dynamodb as dynamodb
import boto3


class ProbeStateRepo:
    def __init__(self):
        self._ensure_schema()
        pass

    def get_probe_state(self, probe_name: str) -> ProbeState:
        pass

    def _ensure_schema(self):
        ddb: dynamodb.ServiceResource = boto3.resource('dynamodb',
                                                       endpoint_url='http://localhost:8000',
                                                       region_name='us-west-2')

        #        ddb.Table(name='probe_state').delete()
        print(list(ddb.tables.all()))

        if self.table_exists(ddb, 'probe_state'):
            return

        tbl = ddb.create_table(
            TableName='probe_state',
            AttributeDefinitions=[
                {
                    'AttributeName': 'probe_name',
                    'AttributeType': 'S'
                },
            ],
            KeySchema=[
                {
                    'AttributeName': 'probe_name',
                    'KeyType': 'HASH'
                },
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        tbl.wait_until_exists()
        tbl.delete()

    def table_exists(self, dd: dynamodb.ServiceResource, table: str) -> bool:
        exists: bool = False
        try:
            tt = dd.Table(name=table)
            tt.load()
            exists = True
        except:
            pass
        return exists
