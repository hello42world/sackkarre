from probe_state import ProbeState
import mypy_boto3_dynamodb as dynamodb
import datetime


class ProbeStateRepo:
    PROBE_STATE_TABLE = 'probe_state'

    def __init__(self,
                 db: dynamodb.ServiceResource):
        self.db = db
        self._ensure_schema()

    def update_probe_with_success(self,
                                  probe_name: str,
                                  probe_value: str):
        ps_tbl = self.db.Table(self.PROBE_STATE_TABLE)
        ps_tbl.put_item(
            Item={
                'probe_name': probe_name,
                'value': probe_value,
                'num_errors': 0,
                'last_error': '',
                'last_updated': self._utc_now()
            }
        )

    def get_probe_state(self, probe_name: str) -> ProbeState:
        pass

    def _ensure_schema(self):
        if self.table_exists(self.PROBE_STATE_TABLE):
            return

        ps_tbl = self.db.create_table(
            TableName=self.PROBE_STATE_TABLE,
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

    def kill_schema(self):
        if self.table_exists(self.PROBE_STATE_TABLE):
            ps_tbl = self.db.Table(self.PROBE_STATE_TABLE)
            ps_tbl.delete()
            ps_tbl.wait_until_not_exists()

    def dump(self):
        for i in self.db.Table(self.PROBE_STATE_TABLE).scan()['Items']:
            print(str(i))

    @staticmethod
    def _utc_now() -> str:
        return datetime.datetime.now(tz=datetime.timezone.utc).replace(microsecond=0).isoformat()