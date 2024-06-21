import unittest
from prober import Prober
import probe_io
import os


def _get_html_fixture(name: str) -> str:
    with open(os.path.dirname(os.path.abspath(__file__)) + f'/fixtures/{name}.html', 'r') as file:
        return file.read()


class TestProber(unittest.TestCase):
    def test_lidl_page(self):
        probe_str = '''
step_templates:
  lidl_xpath: &lidl_xpath
    step_type: XPATH
    expr: "//script[@data-hid='json_data_product']"
  lidl_jpath: &lidl_jpath
    step_type: JPATH
    expr: "$.offers[0].price"

probes:
  - id: 1
    name: TestThing
    url: 'lidl_1'
    steps:
      - *lidl_xpath
      - *lidl_jpath
'''
        p = probe_io.load_from_str(probe_str)
        prober = Prober(_get_html_fixture)
        probe_result = prober.do_probe(p[0])
        self.assertFalse(probe_result.is_error)
        self.assertEqual(139.00, float(probe_result.value))

    def test_lidl_bad_xpath(self):
        probe_str = '''
step_templates:
  lidl_xpath: &lidl_xpath
    step_type: XPATH
    expr: "//script[@data-hid='foobar']"

probes:
  - id: 2
    name: TestThing
    url: 'lidl_1'
    steps:
      - *lidl_xpath
'''
        p = probe_io.load_from_str(probe_str)
        prober = Prober(_get_html_fixture)
        probe_result = prober.do_probe(p[0])
        self.assertTrue(probe_result.is_error)
        self.assertTrue(len(probe_result.error_msg) > 0)


if __name__ == '__main__':
    unittest.main()
