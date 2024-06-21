from probe import Probe
from probe_state_repo import IProbeStateRepo
from prober import IProber
from enum import Enum
from typing import Optional


class TargetChangeType(Enum):
    VALUE_CHANGED = 1
    MAX_ERRORS_REACHED = 2


class TargetChange:
    def __init__(self,
                 change_type: TargetChangeType,
                 old_value: str = '',
                 new_value: str = '',
                 error_msg: str = ''):
        self.change_type = change_type
        self.old_value = old_value
        self.new_value = new_value
        self.error_msg = error_msg


class Scanner:
    MAX_ERRORS = 3

    def __init__(self,
                 probe_state_repo: IProbeStateRepo,
                 prober: IProber):
        self.probe_state_repo = probe_state_repo
        self.prober = prober

    def scan(self, probes: list[Probe]) -> list[TargetChange]:
        res: list[TargetChange] = []
        for probe in probes:
            evt = self.check_probe(probe)
            if evt is not None:
                res.append(evt)
        return res

    def check_probe(self, probe: Probe) -> Optional[TargetChange]:
        ps = self.probe_state_repo.find_state(probe.probe_name)
        change = None
        if ps is None:
            pr = self.prober.do_probe(probe)
            if pr.is_error:
                self.probe_state_repo.update_state_with_failure(probe.probe_name, pr.error_msg)
            else:
                self.probe_state_repo.update_state_with_success(probe.probe_name, pr.value)
        else:
            if ps.num_errors >= self.MAX_ERRORS:
                pass
            else:
                pr = self.prober.do_probe(probe)
                if pr.is_error:
                    if ps.num_errors == self.MAX_ERRORS - 1:
                        change = TargetChange(
                            change_type=TargetChangeType.MAX_ERRORS_REACHED,
                            error_msg=pr.error_msg)
                    self.probe_state_repo.update_state_with_failure(probe.probe_name, pr.error_msg)
                else:
                    if pr.value != ps.value:
                        change = TargetChange(
                            change_type=TargetChangeType.VALUE_CHANGED,
                            old_value=ps.value,
                            new_value=pr.value)
                        self.probe_state_repo.update_state_with_success(probe.probe_name, pr.value)

        return change
