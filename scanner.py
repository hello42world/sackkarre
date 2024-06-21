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
                 probe: Probe,
                 change_type: TargetChangeType,
                 old_value: str = '',
                 new_value: str = '',
                 error_msg: str = ''):
        self.probe = probe
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
        cur_state = self.probe_state_repo.find_state(probe.probe_id)
        change = None
        if cur_state is None:
            probe_result = self.prober.do_probe(probe)
            if probe_result.is_error:
                self.probe_state_repo.update_state_with_failure(probe.probe_id, probe_result.error_msg)
            else:
                self.probe_state_repo.update_state_with_success(probe.probe_id, probe_result.value)
        else:
            if cur_state.num_errors >= self.MAX_ERRORS:
                pass
            else:
                probe_result = self.prober.do_probe(probe)
                if probe_result.is_error:
                    if cur_state.num_errors == self.MAX_ERRORS - 1:
                        change = TargetChange(
                            probe=probe,
                            change_type=TargetChangeType.MAX_ERRORS_REACHED,
                            error_msg=probe_result.error_msg)
                    self.probe_state_repo.update_state_with_failure(probe.probe_id, probe_result.error_msg)
                else:
                    if probe_result.value != cur_state.value:
                        change = TargetChange(
                            probe=probe,
                            change_type=TargetChangeType.VALUE_CHANGED,
                            old_value=cur_state.value,
                            new_value=probe_result.value)
                        self.probe_state_repo.update_state_with_success(probe.probe_id, probe_result.value, cur_state.value)

        return change
