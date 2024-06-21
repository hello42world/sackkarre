from typing import Optional
import mypy_boto3_dynamodb as dynamodb
from abc import abstractmethod
from base_repo import BaseRepo


class IConfigRepo:
    @abstractmethod
    def find_value(self, ken: str) -> Optional[str]:
        pass


class ConfigRepo(IConfigRepo, BaseRepo):
    CONFIG_TABLE_DEFAULT = 'config'

    def __init__(self,
                 db: dynamodb.ServiceResource,
                 table_name: str = CONFIG_TABLE_DEFAULT):
        BaseRepo.__init__(self, db, table_name)

    def find_value(self, key: str) -> Optional[str]:
        ps_tbl = self.db.Table(self.table_name)
        s = ps_tbl.get_item(
            Key={
                'key': key
            },
        )
        if 'Item' not in s.keys():
            return None
        return s['Item']['value']


    def ensure_schema(self) -> None:
        if self.schema_exists():
            return

        tbl = self.db.create_table(
            TableName=self.table_name,
            AttributeDefinitions=[
                {
                    'AttributeName': 'key',
                    'AttributeType': 'S'
                },
            ],
            KeySchema=[
                {
                    'AttributeName': 'key',
                    'KeyType': 'HASH'
                },
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        tbl.wait_until_exists()
