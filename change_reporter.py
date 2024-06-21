from abc import abstractmethod
import mypy_boto3_sns as sns
import boto3

from scanner import TargetChange, TargetChangeType
import aws


class IChangeReporter:
    @abstractmethod
    def report_state_changes(self, change_list: list[TargetChange]) -> None:
        pass


def generate_report(change_list: list[TargetChange]) -> str:
    result = ''
    for c in change_list:
        if c.change_type == TargetChangeType.VALUE_CHANGED:
            result += f'Price changed: "{c.probe.probe_name}" was {c.old_value} now {c.new_value}\n'
            result += f'  See: {c.probe.target_url}\n'
        elif c.change_type == TargetChangeType.MAX_ERRORS_REACHED:
            result += f'Something is wrong with: "{c.probe.probe_name}". Last error: {c.error_msg}\n'
            result += f'  See: {c.probe.target_url}\n'
        result += '\n'
    return result


class StdoutChangeReporter(IChangeReporter):
    def report_state_changes(self, change_list: list[TargetChange]) -> None:
        report = generate_report(change_list)
        print(report)


class AwsSnsChangeReported(IChangeReporter):
    def __init__(self, topic_name: str, aws_region: str):
        self.topic_name = topic_name
        self.aws_region = aws_region

    def report_state_changes(self, change_list: list[TargetChange]) -> None:
        the_sns: sns.ServiceResource = boto3.resource('sns', region_name=self.aws_region)
        topic = the_sns.create_topic(Name=self.topic_name)
        topic.publish(
            Message=generate_report(change_list)
        )
