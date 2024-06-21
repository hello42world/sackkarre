from typing import Optional
import mypy_boto3_dynamodb as dynamodb
from abc import abstractmethod
from base_repo import BaseRepo


class IConfigRepo:
    @abstractmethod
    def find_value(self, key: str) -> Optional[str]:
        pass

    @abstractmethod
    def put_value(self, key: str, value: str) -> None:
        pass


class ConfigRepo(IConfigRepo, BaseRepo):

    def __init__(self,
                 db: dynamodb.ServiceResource,
                 base_name: str):
        BaseRepo.__init__(self, db, base_name + '_config')
        self.tbl = self.db.Table(self.table_name)

    def find_value(self, key: str) -> Optional[str]:
        tbl = self.db.Table(self.table_name)
        s = tbl.get_item(
            Key={
                'key': key
            },
        )
        return s['Item']['value'] if 'Item' in s.keys() else None

    def put_value(self, key: str, value: str) -> None:
        tbl = self.db.Table(self.table_name)
        tbl.put_item(
            Item={
                'key': key,
                'value': value,
            }
        )

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
