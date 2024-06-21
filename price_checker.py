import mypy_boto3_dynamodb as dynamodb
from aiohttp import ClientSession

from scanner import Scanner
from probe_state_repo import ProbeStateRepo
from prober import Prober, IPageLoader
import probe_io
from config_repo import ConfigRepo
from change_reporter import IChangeReporter


class AioHttpPageLoader(IPageLoader):
    async def load_page(self, url: str) -> str:
        async with ClientSession(max_field_size=16384) as session:
            async with session.get(url) as response:
                buf = await response.read()
                return buf.decode('utf-8')



def run_price_check(
        db: dynamodb.ServiceResource,
        base_name: str,
        config_key: str,
        change_reporter: IChangeReporter) -> None:
    cr = ConfigRepo(db, base_name)
    probe_spec_str = cr.find_value(config_key)
    if probe_spec_str is None:
        raise Exception(f'Config key {config_key} not found')
    probes = probe_io.load_from_str(probe_spec_str)
    probe_state_repo = ProbeStateRepo(db, base_name)
    probe_state_repo.ensure_schema()
    prober = Prober(AioHttpPageLoader())
    scanner = Scanner(probe_state_repo, prober)
    changes = scanner.scan(probes)
    if len(changes) > 0:
        change_reporter.report_state_changes(changes)
