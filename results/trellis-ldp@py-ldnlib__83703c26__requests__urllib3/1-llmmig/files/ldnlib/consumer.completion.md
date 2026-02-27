### Explanation of Changes
To migrate the code from using the `requests` library to `urllib3`, the following changes were made:
1. **Importing `urllib3`**: The `requests` library was replaced with `urllib3`, so the `requests` import was removed, and `urllib3` was imported instead.
2. **Creating an HTTP Connection Pool**: Unlike `requests`, `urllib3` requires an explicit `PoolManager` to manage HTTP connections. A `PoolManager` instance was created and used for all HTTP requests.
3. **Replacing `requests.get`**: The `requests.get` calls were replaced with `urllib3.PoolManager.request` calls. The method, headers, and additional parameters were adjusted accordingly.
4. **Handling Response**: The `urllib3` response object differs from `requests`. The response body is accessed using `response.data` (which is in bytes), so it was decoded to a string using `.decode('utf-8')` where necessary.
5. **Error Handling**: The `raise_for_status` method in `requests` was replaced with manual status code checks in `urllib3`. If the status code is not in the 2xx range, an `HTTPError` is raised.

### Modified Code
```python
from rdflib import Graph, URIRef
import urllib3

import json

from .base import BaseLDN


class Consumer(BaseLDN):

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.http = urllib3.PoolManager()  # Create a PoolManager for HTTP requests

    def notifications(self, inbox, **kwargs):
        """
        Retrieve all of the notification IRIs from an ldp:inbox as a list.
        """
        headers = kwargs.pop("headers", dict())
        if 'accept' not in headers:
            headers['accept'] = kwargs.pop("accept", self.accept_headers)

        # Perform the GET request using urllib3
        response = self.http.request("GET", inbox, headers=headers, **kwargs)
        
        # Raise an error if the status code is not 2xx
        if response.status >= 400:
            raise urllib3.exceptions.HTTPError(f"HTTP request failed with status code {response.status}")

        # Parse the response data
        g = Graph().parse(data=response.data.decode('utf-8'), format=self.content_type_to_mime_type(
            response.headers['content-type']))
        return [str(o) for (s, o) in g[:URIRef(self.LDP_CONTAINS)]]

    def notification(self, iri, **kwargs):
        """
        Retrieve a single LDN notification and decode into a Python object.
        """
        headers = kwargs.pop("headers", dict())
        if 'accept' not in headers:
            headers['accept'] = kwargs.pop("accept", self.accept_headers)

        # Perform the GET request using urllib3
        response = self.http.request("GET", iri, headers=headers, **kwargs)
        
        # Raise an error if the status code is not 2xx
        if response.status >= 400:
            raise urllib3.exceptions.HTTPError(f"HTTP request failed with status code {response.status}")

        # Determine the MIME type and parse the response accordingly
        mime_type = self.content_type_to_mime_type(response.headers['content-type'])
        if mime_type == self.JSON_LD:
            return json.loads(response.data.decode('utf-8'))
        else:
            g = Graph().parse(data=response.data.decode('utf-8'), format=mime_type)
            return json.loads(g.serialize(format="json-ld"))
```

### Key Notes
- The `urllib3.PoolManager` instance (`self.http`) is reused for all HTTP requests, which is more efficient than creating a new connection for each request.
- The `response.data` from `urllib3` is in bytes, so it is explicitly decoded to a string using `.decode('utf-8')` before further processing.
- Error handling is implemented manually by checking the `response.status` code, as `urllib3` does not have a built-in `raise_for_status` method like `requests`.