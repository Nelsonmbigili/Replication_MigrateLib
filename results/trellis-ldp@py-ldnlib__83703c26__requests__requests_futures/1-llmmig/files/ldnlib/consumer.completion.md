### Explanation of Changes:
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `requests_futures.sessions` to use the `FuturesSession` class.
2. **Session Initialization**: Created an instance of `FuturesSession` to handle asynchronous requests.
3. **Request Method Changes**: Replaced `requests.get` with `session.get` (where `session` is an instance of `FuturesSession`).
4. **Response Handling**: Since `requests_futures` returns a `Future` object, the `.result()` method is called on the response to retrieve the actual `Response` object before processing it.

These changes ensure that the code now uses `requests_futures` for asynchronous HTTP requests while maintaining the original functionality.

---

### Modified Code:
```python
from rdflib import Graph, URIRef
from requests_futures.sessions import FuturesSession

import json

from .base import BaseLDN


class Consumer(BaseLDN):

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.session = FuturesSession()  # Initialize FuturesSession for async requests

    def notifications(self, inbox, **kwargs):
        """
        Retrieve all of the notification IRIs from an ldp:inbox as a list.
        """
        headers = kwargs.pop("headers", dict())
        if 'accept' not in headers:
            headers['accept'] = kwargs.pop("accept", self.accept_headers)

        future = self.session.get(inbox, headers=headers, **kwargs)  # Use session.get for async request
        r = future.result()  # Retrieve the actual Response object
        r.raise_for_status()
        g = Graph().parse(data=r.text, format=self.content_type_to_mime_type(
            r.headers['content-type']))
        return [str(o) for (s, o) in g[:URIRef(self.LDP_CONTAINS)]]

    def notification(self, iri, **kwargs):
        """
        Retrieve a single LDN notification and decode into a Python object.
        """
        headers = kwargs.pop("headers", dict())
        if 'accept' not in headers:
            headers['accept'] = kwargs.pop("accept", self.accept_headers)

        future = self.session.get(iri, headers=headers, **kwargs)  # Use session.get for async request
        r = future.result()  # Retrieve the actual Response object
        r.raise_for_status()
        mime_type = self.content_type_to_mime_type(r.headers['content-type'])
        if mime_type == self.JSON_LD:
            return r.json()
        else:
            g = Graph().parse(data=r.text, format=mime_type)
            return json.loads(g.serialize(format="json-ld"))
```

---

### Key Notes:
- The `FuturesSession` class from `requests_futures` is used to handle asynchronous requests.
- The `.result()` method is called on the `Future` object returned by `session.get` to block and retrieve the `Response` object, ensuring compatibility with the original synchronous logic.
- No other parts of the code were modified, as per the instructions.