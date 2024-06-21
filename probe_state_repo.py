from typing import Optional
from probe_state import ProbeState
import mypy_boto3_dynamodb as dynamodb
import datetime
from dateutil import parser
from abc import abstractmethod


class IProbeStateRepo:
    @abstractmethod
    def find_state(self, probe_name: str) -> Optional[ProbeState]:
        pass

    @abstractmethod
    def update_state_with_success(self, probe_name: str, probe_value: str) -> None:
        pass

    @abstractmethod
    def update_state_with_failure(self, probe_name: str, error_msg: str) -> None:
        pass


class ProbeStateRepo(IProbeStateRepo):
    PROBE_STATE_TABLE_DEFAULT = 'probe_state'

    def __init__(self,
                 db: dynamodb.ServiceResource,
                 table_name: str = PROBE_STATE_TABLE_DEFAULT,
                 consistent_read: bool = False):
        self.db = db
        self.table_name = table_name
        self.consistent_read = consistent_read

    def find_state(self, probe_name: str) -> Optional[ProbeState]:
        ps_tbl = self.db.Table(self.table_name)
        s = ps_tbl.get_item(
            Key={
                'probe_name': probe_name
            },
            ConsistentRead=self.consistent_read
        )
        if 'Item' not in s.keys():
            return None
        item = s['Item']
        return ProbeState(
            probe_name=item['probe_name'],
            value=item['value'],
            num_errors=item['num_errors'],
            last_error=item['last_error'],
            last_updated=parser.parse(item['last_updated'])
        )

    def update_state_with_success(self, probe_name: str, probe_value: str) -> None:
        ps_tbl = self.db.Table(self.table_name)
        ps_tbl.put_item(
            Item={
                'probe_name': probe_name,
                'value': probe_value,
                'num_errors': 0,
                'last_error': '',
                'last_updated': self._utc_now()
            }
        )

    def update_state_with_failure(self, probe_name: str, error_msg: str) -> None:
        ps_tbl = self.db.Table(self.table_name)
        ps_tbl.update_item(
            Key={
                'probe_name': probe_name,
            },
            UpdateExpression="""SET 
                last_error = :last_error, 
                #value=if_not_exists(#value, :empty_str), 
                last_updated = :last_updated, num_errors=if_not_exists(num_errors, :zero) + :inc""",
            ExpressionAttributeValues={
                ':last_error': error_msg,
                ':last_updated': self._utc_now(),
                ':empty_str': '',
                ':inc': 1,
                ':zero': 0,
            },
            ExpressionAttributeNames={
                '#value': 'value'
            }
        )

    def ensure_schema(self) -> None:
        if self.table_exists(self.table_name):
            return

        ps_tbl = self.db.create_table(
            TableName=self.table_name,
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
        ps_tbl.wait_until_exists()

    def table_exists(self, table: str) -> bool:
        exists: bool = False
        try:
            tt = self.db.Table(name=table)
            tt.load()
            exists = True
        except:
            pass
        return exists

    def kill_schema(self) -> None:
        if self.table_exists(self.table_name):
            ps_tbl = self.db.Table(self.table_name)
            ps_tbl.delete()
            ps_tbl.wait_until_not_exists()

    def dump(self) -> None:
        for i in self.db.Table(self.table_name).scan()['Items']:
            print(str(i))

    @staticmethod
    def _utc_now() -> str:
        return datetime.datetime.now(tz=datetime.timezone.utc).replace(microsecond=0).isoformat()
