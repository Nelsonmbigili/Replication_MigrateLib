### Explanation of Changes
To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Importing `urllib3`**: The `requests` library was replaced with `urllib3`. The `requests` library is a higher-level abstraction over HTTP requests, while `urllib3` is a lower-level library that requires more manual handling of connections and responses.

2. **Creating a PoolManager**: In `urllib3`, you need to create a `PoolManager` instance to manage connections. This was added to handle the HTTP requests.

3. **Making GET Requests**: The `requests.get()` method was replaced with `http.request('GET', ...)` where `http` is the `PoolManager` instance.

4. **Handling Responses**: The response handling was adjusted to use `response.data` instead of `response.text`, and the status code check was done using `response.status`.

5. **Headers**: The headers were passed in a slightly different format, as `urllib3` requires them to be a dictionary.

6. **JSON Handling**: The JSON response handling was updated to use `json.loads()` directly on the response data.

Here is the modified code:

```python
from rdflib import Graph, URIRef
import urllib3
import json

from .base import BaseLDN

class Consumer(BaseLDN):

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.http = urllib3.PoolManager()

    def notifications(self, inbox, **kwargs):
        """
        Retrieve all of the notification IRIs from an ldp:inbox as a list.
        """
        headers = kwargs.pop("headers", dict())
        if 'accept' not in headers:
            headers['accept'] = kwargs.pop("accept", self.accept_headers)

        response = self.http.request('GET', inbox, headers=headers, **kwargs)
        response.raise_for_status()
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

        response = self.http.request('GET', iri, headers=headers, **kwargs)
        response.raise_for_status()
        mime_type = self.content_type_to_mime_type(response.headers['content-type'])
        if mime_type == self.JSON_LD:
            return json.loads(response.data.decode('utf-8'))
        else:
            g = Graph().parse(data=response.data.decode('utf-8'), format=mime_type)
            return json.loads(g.serialize(format="json-ld"))
```