import probe
import probe_result
import typing
import json
import jsonpath_ng
from lxml import etree


class Prober:
    def __init__(self,
                 url_loader: typing.Callable[[str], str]):
        self.url_loader = url_loader

    def do_probe(self, p: probe.Probe) -> probe_result.ProbeResult:
        result = probe_result.ProbeResult(p)
        try:
            result.result = self._do_probe(p)
        except Exception as exc:
            result.is_error = True
            result.error_msg = str(exc)
        return result

    def _do_probe(self, p: probe.Probe) -> str:
        # Get the page
        data = self.url_loader(p.url)
        # with urllib.request.urlopen(p.url) as response:
        #    data = response.read()
        for s in p.steps:
            if s.step_type == probe.ProbeStepType.XPATH:
                data = self._step_xpath(data, s.expr)
            elif s.step_type == probe.ProbeStepType.JPATH:
                data = self._step_jpath(data, s.expr)
            else:
                raise Exception("Unknown step type")
        return data


    def _step_xpath(self, data: str, xpath: str) -> str:
        parser = etree.HTMLParser()
        doc = etree.fromstring(data, parser)
        res: list = doc.xpath(xpath)
        if len(res) == 0:
            raise Exception(f'Xpath {xpath} found nothing')
        return res[0].text


    def _step_jpath(self, data: str, jpath: str) -> str:
        json_data = json.loads(data)
        json_path = jsonpath_ng.parse(jpath)
        match: list = json_path.find(json_data)
        if len(match) == 0:
            raise Exception(f'Jpath {jpath} found nothing')
        return match[0].value
