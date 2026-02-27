### Explanation of Changes:
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `requests_futures.sessions` to use the `FuturesSession` class.
2. **Session Initialization**: Created an instance of `FuturesSession` to handle asynchronous requests.
3. **Method Adjustments**:
   - Replaced `requests.options` with `session.options` for the `OPTIONS` request.
   - Replaced `requests.post` with `session.post` for the `POST` request.
   - Since `requests_futures` returns a `Future` object, the `.result()` method is called to get the actual response object where necessary.
4. **Behavior Preservation**: Ensured that the behavior of the original code remains unchanged by calling `.result()` immediately after making the requests, effectively making the requests synchronous (as in the original code).

### Modified Code:
```python
from rdflib import Graph
from requests_futures.sessions import FuturesSession

import ipaddress
import json
import socket
from urllib.parse import urlparse

from .base import BaseLDN


class Sender(BaseLDN):

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.allow_localhost = kwargs.get('allow_localhost', False)
        self.session = FuturesSession()  # Initialize FuturesSession

    def __accept_post_options(self, inbox, **kwargs):
        r = self.session.options(inbox, **kwargs).result()  # Use session.options and call .result()
        if r.status_code == requests.codes.ok and 'accept-post' in r.headers:
            if self.JSON_LD in r.headers['accept-post']:
                return self.JSON_LD

            for content_type in r.headers['accept-post'].split(','):
                return self.content_type_to_mime_type(content_type)

    def __is_localhost(self, inbox):
        return ipaddress.ip_address(socket.gethostbyname(
            urlparse(inbox).hostname)).is_loopback

    def __post_message(self, inbox, data, content_type, **kwargs):
        if self.allow_localhost or not self.__is_localhost(inbox):
            headers = kwargs.pop("headers", dict())
            headers['content-type'] = content_type
            r = self.session.post(inbox, data=data, headers=headers, **kwargs).result()  # Use session.post and call .result()
            r.raise_for_status()
        else:
            raise ValueError("Invalid local inbox.")

    def send(self, inbox, data, **kwargs):
        """Send the provided data to an inbox."""
        if isinstance(data, dict) or isinstance(data, list):
            self.__post_message(inbox, json.dumps(data), self.JSON_LD,
                                **kwargs)
        elif isinstance(data, str):
            self.__post_message(inbox, data, self.JSON_LD, **kwargs)
        elif isinstance(data, Graph):
            ct = self.__accept_post_options(inbox, **kwargs) or self.JSON_LD
            self.__post_message(inbox, data.serialize(format=ct), ct,
                                **kwargs)
        else:
            raise TypeError(
                    "You cannot send data of type {}.".format(type(data)))
```

### Summary of Changes:
- Replaced `requests` with `requests_futures.sessions.FuturesSession`.
- Used `session.options` and `session.post` for making requests.
- Called `.result()` on the `Future` objects to maintain synchronous behavior.