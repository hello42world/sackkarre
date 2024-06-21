import boto3
import unittest
import probe_state_repo


class TestProbeStateRepo(unittest.TestCase):
    def test_1(self):
        db = boto3.resource('dynamodb',
                            endpoint_url='http://localhost:8000')
        repo = probe_state_repo.ProbeStateRepo(db, 'test_psr', True)
        repo.kill_schema()
        repo.ensure_schema()
        self.assertIsNone(repo.find_state('foo'))
        repo.update_state_with_success('foo', '37')
        s = repo.find_state('foo')
        self.assertEqual('foo', s.probe_name)
        self.assertEqual('37', s.value)
        self.assertEqual(0, s.num_errors)
        self.assertFalse(s.has_error)
        repo.update_state_with_failure('foo', 'boom')
        s = repo.find_state('foo')
        self.assertEqual('foo', s.probe_name)
        self.assertEqual(1, s.num_errors)
        self.assertTrue(s.has_error)
        self.assertEqual('boom', s.last_error)
        repo.update_state_with_failure('foo', 'boom')
        s = repo.find_state('foo')
        self.assertEqual(2, s.num_errors)
