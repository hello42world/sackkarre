

class ProbeState:
    def __init__(self,
                 probe_name: str,
                 num_errors: int = 0,
                 last_error: str = '',
                 last_value: str = ''):
        self.probe_name = probe_name
        self.num_errors = num_errors
        self.last_error = last_error
        self.last_value = last_value

    @property
    def has_error(self):
        return self.num_errors > 0