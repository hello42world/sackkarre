import unittest
import probe_io


class TestProbeIO(unittest.TestCase):

    def testUniqueId(self):
        probe_str = '''
probes:
  - id: "1"
    name: Battery 4ah
    url: 'https://www.lidl.de/p/parkside-20-v-akku-pap-20-b3-4-ah/p100367574'
    steps: []
    
    - id: "1"
    name: Something else
    url: 'https://www.lidl.de/p/foo/p100367574'
    steps: []
        '''
        with self.assertRaises(Exception):
            probe_io.load_from_str(probe_str)
