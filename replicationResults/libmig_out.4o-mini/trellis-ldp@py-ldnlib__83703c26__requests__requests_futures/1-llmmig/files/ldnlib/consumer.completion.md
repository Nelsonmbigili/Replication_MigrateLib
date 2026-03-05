### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, I made the following changes:

1. **Import Statement**: I replaced the import of `requests` with `from requests_futures.sessions import FuturesSession`. This allows us to use the `FuturesSession` class, which supports asynchronous requests.
  
2. **Session Initialization**: I created an instance of `FuturesSession` instead of using `requests` directly. This allows us to send requests asynchronously.

3. **Asynchronous Request Handling**: I modified the request calls to use the `session.get()` method, which returns a `Future` object. I then called `.result()` on the `Future` object to get the response, which is necessary to retrieve the actual response data.

4. **Error Handling**: The error handling with `raise_for_status()` remains the same, but it is now called on the result of the `Future` object.

Here is the modified code:

```python
from rdflib import Graph, URIRef
from requests_futures.sessions import FuturesSession

import json

from .base import BaseLDN


class Consumer(BaseLDN):

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.session = FuturesSession()

    def notifications(self, inbox, **kwargs):
        """
        Retrieve all of the notification IRIs from an ldp:inbox as a list.
        """
        headers = kwargs.pop("headers", dict())
        if 'accept' not in headers:
            headers['accept'] = kwargs.pop("accept", self.accept_headers)

        future = self.session.get(inbox, headers=headers, **kwargs)
        r = future.result()
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

        future = self.session.get(iri, headers=headers, **kwargs)
        r = future.result()
        r.raise_for_status()
        mime_type = self.content_type_to_mime_type(r.headers['content-type'])
        if mime_type == self.JSON_LD:
            return r.json()
        else:
            g = Graph().parse(data=r.text, format=mime_type)
            return json.loads(g.serialize(format="json-ld"))
```