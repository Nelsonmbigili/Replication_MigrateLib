### Explanation of Changes
To migrate the code from using the `requests` library to `urllib3`, the following changes were made:
1. **Importing `urllib3`**: The `requests` library was removed, and `urllib3` was imported instead.
2. **HTTP Methods**: The `requests.options` and `requests.post` calls were replaced with equivalent `urllib3` methods using an `urllib3.PoolManager` instance.
3. **Status Codes**: The `requests.codes.ok` was replaced with the equivalent HTTP status code `200`.
4. **Headers Handling**: The `urllib3` library requires headers to be passed explicitly in the request methods.
5. **Error Handling**: The `requests.raise_for_status()` method was replaced with manual status code checks, as `urllib3` does not provide a direct equivalent.
6. **Session Management**: A `urllib3.PoolManager` instance was used to manage HTTP connections.

### Modified Code
```python
from rdflib import Graph
import urllib3

import ipaddress
import json
import socket
from urllib.parse import urlparse

from .base import BaseLDN


class Sender(BaseLDN):

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.allow_localhost = kwargs.get('allow_localhost', False)
        self.http = urllib3.PoolManager()  # Initialize a PoolManager for HTTP requests

    def __accept_post_options(self, inbox, **kwargs):
        response = self.http.request('OPTIONS', inbox, **kwargs)
        if response.status == 200 and 'accept-post' in response.headers:
            if self.JSON_LD in response.headers['accept-post']:
                return self.JSON_LD

            for content_type in response.headers['accept-post'].split(','):
                return self.content_type_to_mime_type(content_type)

    def __is_localhost(self, inbox):
        return ipaddress.ip_address(socket.gethostbyname(
            urlparse(inbox).hostname)).is_loopback

    def __post_message(self, inbox, data, content_type, **kwargs):
        if self.allow_localhost or not self.__is_localhost(inbox):
            headers = kwargs.pop("headers", dict())
            headers['Content-Type'] = content_type
            response = self.http.request(
                'POST',
                inbox,
                body=data,
                headers=headers,
                **kwargs
            )
            if response.status < 200 or response.status >= 300:
                raise urllib3.exceptions.HTTPError(
                    f"HTTP request failed with status code {response.status}"
                )
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

### Key Notes
- The `urllib3.PoolManager` instance (`self.http`) is used to manage HTTP connections.
- The `urllib3` library does not have a `raise_for_status()` method, so manual status code checks were added to handle HTTP errors.
- The `headers` dictionary was updated to use `Content-Type` instead of `content-type` to align with HTTP header conventions.
- The rest of the code remains unchanged to ensure compatibility with the larger application.