import datetime


class ProbeState:
    def __init__(self,
                 probe_name: str,
                 value: str = '',
                 num_errors: int = 0,
                 last_error: str = '',
                 last_updated: datetime.datetime = None):
        self.probe_name = probe_name
        self.value = value
        self.num_errors = num_errors
        self.last_error = last_error
        self.last_updated = last_updated

    @property
    def has_error(self):
        return self.num_errors > 0