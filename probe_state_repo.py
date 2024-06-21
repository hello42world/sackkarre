from typing import Optional
from probe_state import ProbeState
import mypy_boto3_dynamodb as dynamodb
import datetime
from dateutil import parser
from abc import abstractmethod
from base_repo import BaseRepo


class IProbeStateRepo:
    @abstractmethod
    def find_state(self, probe_id: str) -> Optional[ProbeState]:
        pass

    @abstractmethod
    def update_state_with_success(self, probe_id: str, probe_value: str) -> None:
        pass

    @abstractmethod
    def update_state_with_failure(self, probe_id: str, error_msg: str) -> None:
        pass


class ProbeStateRepo(IProbeStateRepo, BaseRepo):
    def __init__(self,
                 db: dynamodb.ServiceResource,
                 base_name: str,
                 consistent_read: bool = False):
        BaseRepo.__init__(self, db, base_name + '_probe_state')
        self.consistent_read = consistent_read

    def find_state(self, probe_id: str) -> Optional[ProbeState]:
        ps_tbl = self.db.Table(self.table_name)
        s = ps_tbl.get_item(
            Key={
                'probe_id': probe_id
            },
            ConsistentRead=self.consistent_read
        )
        if 'Item' not in s.keys():
            return None
        item = s['Item']
        return ProbeState(
            probe_id=item['probe_id'],
            value=item['value'],
            num_errors=item['num_errors'],
            last_error=item['last_error'],
            last_updated=parser.parse(item['last_updated'])
        )

    def update_state_with_success(self, probe_id: str, probe_value: str) -> None:
        ps_tbl = self.db.Table(self.table_name)
        ps_tbl.put_item(
            Item={
                'probe_id': probe_id,
                'value': str(probe_value),
                'num_errors': 0,
                'last_error': '',
                'last_updated': self._utc_now()
            }
        )

    def update_state_with_failure(self, probe_id: str, error_msg: str) -> None:
        ps_tbl = self.db.Table(self.table_name)
        ps_tbl.update_item(
            Key={
                'probe_id': probe_id,
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
        if self.schema_exists():
            return

        ps_tbl = self.db.create_table(
            TableName=self.table_name,
            AttributeDefinitions=[
                {
                    'AttributeName': 'probe_id',
                    'AttributeType': 'S'
                },
            ],
            KeySchema=[
                {
                    'AttributeName': 'probe_id',
                    'KeyType': 'HASH'
                },
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        ps_tbl.wait_until_exists()

    @staticmethod
    def _utc_now() -> str:
        return datetime.datetime.now(tz=datetime.timezone.utc).replace(microsecond=0).isoformat()
