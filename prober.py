import probe
import probe_result
import urllib.request


class Prober:
    def do_probe(self, p: probe.Probe) -> probe_result.ProbeResult:
        pass

    def _do_probe(self, p: probe.Probe) -> str:
        # Get the page
        with urllib.request.urlopen(p.url) as response:
            data = response.read()
        for s in p.steps:
            if s.step_type == probe.ProbeStepType.XPATH:
                data = self._step_xpath(data, s.expr)
            elif s.step_type == probe.ProbeStepType.JPATH:
                data = self._step_jpath(data, s.expr)
            else:
                raise "Unknown step type"
        return data

    def _step_xpath(self, data: str, xpath: str) -> str:
        pass

    def _step_jpath(self, data: str, jpath: str) -> str:
        pass
