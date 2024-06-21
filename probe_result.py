from probe import Probe


class ProbeResult:
    def __init__(self,
                 the_probe: Probe,
                 result: str = '',
                 is_error: bool = False,
                 error_msg: str = ''):
        self.the_probe = the_probe
        self.result = result
        self.is_error = is_error
        self.error_msg = error_msg
