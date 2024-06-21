from enum import Enum
import yaml


class ProbeStepType(Enum):
    XPATH = 1
    JPATH = 2


class ProbeStep:
    def __init__(self,
                 step_type: ProbeStepType,
                 expr: str):
        self.step_type = step_type
        self.expr = expr


class Probe:
    def __init__(self,
                 name: str,
                 url: str,
                 steps: list[ProbeStep]):
        self.name = name
        self.url = url
        self.steps = steps


def load(probe_file: str) -> list[Probe]:
    with open(probe_file, 'r') as file:
        probe_data = yaml.safe_load(file)
    result: list[Probe] = []
    # todo: Name must be unique
    for probe in probe_data['probes']:
        steps: list[ProbeStep] = []
        for step in probe['steps']:
            steps.append(ProbeStep(
                step_type=ProbeStepType[step['step_type']],
                expr=step['expr']))
        result.append(Probe(
            name=probe['name'],
            url=probe['url'],
            steps=steps
        ))
    return result
