from enum import Enum


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
                 target_url: str,
                 steps: list[ProbeStep]):
        self.probe_name = name
        self.target_url = target_url
        self.steps = steps
