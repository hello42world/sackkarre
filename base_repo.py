import mypy_boto3_dynamodb as dynamodb
import boto3


class BaseRepo:
    def __init__(self,
                 db: dynamodb.ServiceResource,
                 table_name: str):
        self.db = db
        self.table_name = table_name

    def schema_exists(self) -> bool:
        exists: bool = False
        try:
            tt = self.db.Table(name=self.table_name)
            tt.load()
            exists = True
        except:
            pass
        return exists

    def kill_schema(self) -> None:
        if self.schema_exists():
            ps_tbl = self.db.Table(self.table_name)
            ps_tbl.delete()
            ps_tbl.wait_until_not_exists()

    def dump(self) -> None:
        for i in self.db.Table(self.table_name).scan()['Items']:
            print(str(i))
