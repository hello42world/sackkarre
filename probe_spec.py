from enum import Enum
import yaml


class StepType(Enum):
    XPATH = 1
    JPATH = 2


class StepSpec:
    def __init__(self,
                 step_type: StepType,
                 expr: str):
        self.step_type = step_type
        self.expr = expr


class ProbeSpec:
    def __init__(self,
                 name: str,
                 url: str,
                 steps: list[StepSpec]):
        self.name = name
        self.url = url
        self.steps = steps


def load(spec_file: str) -> list[ProbeSpec]:
    with open(spec_file, 'r') as file:
        spec = yaml.safe_load(file)
    result: list[ProbeSpec] = []
    for probe in spec['probes']:
        steps: list[StepSpec] = []
        for step in probe['steps']:
            steps.append(StepSpec(
                step_type=StepType[step['step_type']],
                expr=step['expr']))
        result.append(ProbeSpec(
            name=probe['name'],
            url=probe['url'],
            steps=steps
        ))
    return result
