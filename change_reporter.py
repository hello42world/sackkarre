from abc import abstractmethod
from scanner import TargetChange, TargetChangeType


class IChangeReporter:
    @abstractmethod
    def report_state_changes(self, change_list: list[TargetChange]) -> None:
        pass


class StdoutChangeReporter(IChangeReporter):
    def report_state_changes(self, change_list: list[TargetChange]) -> None:
        result = ''
        for c in change_list:
            if c.change_type == TargetChangeType.VALUE_CHANGED:
                result += f'Price changed: {c.probe.probe_name} was {c.old_value} now {c.new_value}\n'
                result += f'  See: {c.probe.target_url}\n'
            elif c.change_type == TargetChangeType.MAX_ERRORS_REACHED:
                result += f'Something is wrong with: {c.probe.probe_name}. Last error: {c.error_msg}\n'
                result += f'  See: {c.probe.target_url}\n'
            result += '\n'

        print(result)
