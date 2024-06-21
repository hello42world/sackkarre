import unittest
from prober import Prober
import probe
import os


def _get_html_fixture(name: str) -> str:
    with open(os.path.dirname(os.path.abspath(__file__)) + f'/fixtures/{name}.html', 'r') as file:
        return file.read()


class MyTestCase(unittest.TestCase):
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
  - name: TestThing
    url: 'lidl_1'
    steps:
      - *lidl_xpath
      - *lidl_jpath
'''
        p = probe.load_from_str(probe_str)
        prober = Prober(_get_html_fixture)
        probe_result = prober.do_probe(p[0])
        self.assertFalse(probe_result.is_error)
        self.assertEqual(139.00, float(probe_result.result))

    def test_lidl_bad_xpath(self):
            probe_str = '''
        step_templates:
          lidl_xpath: &lidl_xpath
            step_type: XPATH
            expr: "//script[@data-hid='foobar']"

        probes:
          - name: TestThing
            url: 'lidl_1'
            steps:
              - *lidl_xpath
        '''
            p = probe.load_from_str(probe_str)
            prober = Prober(_get_html_fixture)
            probe_result = prober.do_probe(p[0])
            self.assertTrue(probe_result.is_error)
            self.assertTrue(len(probe_result.error_msg) > 0)


if __name__ == '__main__':
    unittest.main()
