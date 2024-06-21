import unittest
from typing import Optional

from probe import Probe
import probe_result
from probe_state import ProbeState
from scanner import Scanner, TargetChangeType
from prober import IProber
from probe_state_repo import IProbeStateRepo
from probe_result import ProbeResult


class FakeProber(IProber):

    def __init__(self, res: ProbeResult):
        self.res = res

    def do_probe(self, p: Probe) -> probe_result.ProbeResult:
        return self.res


class FakeProbeStateRepo(IProbeStateRepo):
    def __init__(self, state: ProbeState = None):
        self.state = state
        self.success_called = False
        self.failure_called = False

    def find_state(self, probe_id: str) -> Optional[ProbeState]:
        return self.state

    def update_state_with_success(self, probe_id: str, probe_value: str, old_value: str = '') -> None:
        self.success_called = True

    def update_state_with_failure(self, probe_id: str, error_msg: str) -> None:
        self.failure_called = True


class TestProber(unittest.TestCase):
    def test_new_probe_success(self):
        state_repo = FakeProbeStateRepo()
        probe = Probe('1', 'foo', 'http://foo.foo', [])
        prober = FakeProber(ProbeResult(the_probe=probe, value='42'))
        scanner = Scanner(state_repo, prober)
        target_event = scanner.check_probe(probe)
        self.assertTrue(state_repo.success_called)
        self.assertFalse(state_repo.failure_called)
        self.assertIsNone(target_event)

    def test_new_probe_fail(self):
        state_repo = FakeProbeStateRepo()
        probe = Probe('1', 'foo', 'http://foo.foo', [])
        prober = FakeProber(ProbeResult(the_probe=probe, is_error=True, error_msg='boom'))
        target_event = Scanner(state_repo, prober).check_probe(probe)
        self.assertFalse(state_repo.success_called)
        self.assertTrue(state_repo.failure_called)
        self.assertIsNone(target_event)

    def test_old_probe_changed(self):
        state_repo = FakeProbeStateRepo(state=ProbeState(probe_id='foo', value='43'))
        probe = Probe('1', 'foo', 'http://foo.foo', [])
        prober = FakeProber(ProbeResult(the_probe=probe, value='42'))
        target_event = Scanner(state_repo, prober).check_probe(probe)
        self.assertTrue(state_repo.success_called)
        self.assertFalse(state_repo.failure_called)
        self.assertEqual(TargetChangeType.VALUE_CHANGED, target_event.change_type)
        self.assertEqual('43', target_event.old_value)
        self.assertEqual('42', target_event.new_value)

    def test_old_probe_not_changed(self):
        state_repo = FakeProbeStateRepo(state=ProbeState(probe_id='foo', value='42'))
        probe = Probe('1', 'foo', 'http://foo.foo', [])
        prober = FakeProber(ProbeResult(the_probe=probe, value='42'))
        target_event = Scanner(state_repo, prober).check_probe(probe)
        self.assertFalse(state_repo.success_called)
        self.assertFalse(state_repo.failure_called)
        self.assertIsNone(target_event)

    def test_error_limit_reached(self):
        state_repo = FakeProbeStateRepo(state=ProbeState(probe_id='foo', num_errors=Scanner.MAX_ERRORS - 1))
        probe = Probe('1', 'foo', 'http://foo.foo', [])
        prober = FakeProber(ProbeResult(the_probe=probe, is_error=True, error_msg='boom!'))
        target_event = Scanner(state_repo, prober).check_probe(probe)
        self.assertFalse(state_repo.success_called)
        self.assertTrue(state_repo.failure_called)
        self.assertEqual(TargetChangeType.MAX_ERRORS_REACHED, target_event.change_type)
        self.assertEqual('boom!', target_event.error_msg)


if __name__ == '__main__':
    unittest.main()
