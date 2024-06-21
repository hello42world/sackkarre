from probe import Probe, ProbeStep, ProbeStepType
import yaml


def load_from_str(probe_str: str) -> list[Probe]:
    probe_data = yaml.safe_load(probe_str)
    result: list[Probe] = []
    ids = set()
    for p in probe_data['probes']:
        if p['id'] in ids:
            raise Exception(f'Duplicate probe id {p["id"]}')
        ids.add(p['id'])
        steps: list[ProbeStep] = []
        for step in p['steps']:
            steps.append(ProbeStep(
                step_type=ProbeStepType[step['step_type']],
                expr=step['expr']))
        result.append(Probe(
            probe_id=p['id'],
            probe_name=p['name'],
            target_url=p['url'],
            steps=steps
        ))
    return result


def load_from_file(probe_file: str) -> list[Probe]:
    with open(probe_file, 'r') as file:
        probe_str = file.read()
    return load_from_str(probe_str)
