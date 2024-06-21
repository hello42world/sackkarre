import probe
import probe_result
import typing
import json
import jsonpath_ng
from lxml import etree
from abc import abstractmethod


class IPageLoader:
    @abstractmethod
    async def load_page(self, url: str) -> str:
        pass


class IProber:
    @abstractmethod
    async def do_probe(self, p: probe.Probe) -> probe_result.ProbeResult:
        pass


class Prober(IProber):
    def __init__(
            self,
            page_loader: IPageLoader):
        self.page_loader = page_loader

    async def do_probe(self, p: probe.Probe) -> probe_result.ProbeResult:
        result = probe_result.ProbeResult(p)
        try:
            html_page = await self.page_loader.load_page(p.target_url)
            result.value = self._do_probe(p, html_page)
        except Exception as exc:
            result.is_error = True
            result.error_msg = str(exc)
        return result

    def _do_probe(self, p: probe.Probe, page_html: str) -> str:
        data = page_html
        for s in p.steps:
            if s.step_type == probe.ProbeStepType.XPATH:
                data = self._step_xpath(data, s.expr)
            elif s.step_type == probe.ProbeStepType.JPATH:
                data = self._step_jpath(data, s.expr)
            else:
                raise Exception("Unknown step type")
        return str(data)

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
