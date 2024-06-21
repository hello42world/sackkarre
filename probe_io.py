from probe import Probe, ProbeStep, ProbeStepType
import yaml


def load_from_str(probe_str: str) -> list[Probe]:
    probe_data = yaml.safe_load(probe_str)
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
            target_url=probe['url'],
            steps=steps
        ))
    return result


def load_from_file(probe_file: str) -> list[Probe]:
    with open(probe_file, 'r') as file:
        probe_str = file.read()
    return load_from_str(probe_str)
