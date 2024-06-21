import mypy_boto3_dynamodb as dynamodb
import urllib.request

from scanner import Scanner
from probe_state_repo import ProbeStateRepo
from prober import Prober
import probe_io
from config_repo import ConfigRepo
from change_reporter import IChangeReporter


def get_url(url: str) -> str:
    with urllib.request.urlopen(url) as file:
        return file.read()



def run_price_check(
        db: dynamodb.ServiceResource,
        config_key: str,
        change_reporter: IChangeReporter) -> None:
    cr = ConfigRepo(db=db)
    probe_spec_str = cr.find_value(config_key)
    if probe_spec_str is None:
        raise Exception(f'Config key {config_key} not found')
    probes = probe_io.load_from_str(probe_spec_str)
    probe_state_repo = ProbeStateRepo(db)
    probe_state_repo.ensure_schema()
    prober = Prober(get_url)
    scanner = Scanner(probe_state_repo, prober)
    changes = scanner.scan(probes)
    if len(changes) > 0:
        change_reporter.report_state_changes(changes)

