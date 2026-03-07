from typing import Any


class ApiException(Exception):
    def __init__(self, data: Any = None, headers: dict = None, status_code: int = None, *args, **kwargs):
        self.data = data or kwargs
        self.headers = headers
        self.status_code = status_code


class ConfigurationException(Exception):
    pass
