from typing import Any
from requests_futures.sessions import FuturesSession
from requests.structures import CaseInsensitiveDict


class ApiException(Exception):
    def __init__(self, data: Any = None, headers: CaseInsensitiveDict = None, status_code: int = None, *args, **kwargs):
        self.data = data or kwargs
        self.headers = headers
        self.status_code = status_code


class ConfigurationException(Exception):
    pass

# Example of how to use FuturesSession (not part of the original code)
session = FuturesSession()
# You can now use session to make asynchronous requests
# response_future = session.get('http://example.com')
