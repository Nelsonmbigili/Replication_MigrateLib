### Explanation of Changes
To migrate the code from using the `requests` library to the `treq` library, the following changes were made:

1. **Import Statement**: The import statement for `requests` was replaced with `import treq`.
2. **GET Requests**: The `requests.get()` method was replaced with `treq.get()`. The usage remains similar, but `treq` handles the response differently.
3. **Response Handling**: The response object from `treq` does not have a `.text` attribute. Instead, we use `response.content` to get the raw response data. Additionally, `treq` provides a `.json()` method to directly parse JSON responses.
4. **Error Handling**: The `raise_for_status()` method is not available in `treq`. Instead, we check the response status code and raise an exception if it indicates an error.

Here is the modified code:

```python
from rdflib import Graph, URIRef
import treq

import json

from .base import BaseLDN


class Consumer(BaseLDN):

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

    def notifications(self, inbox, **kwargs):
        """
        Retrieve all of the notification IRIs from an ldp:inbox as a list.
        """
        headers = kwargs.pop("headers", dict())
        if 'accept' not in headers:
            headers['accept'] = kwargs.pop("accept", self.accept_headers)

        r = treq.get(inbox, headers=headers, **kwargs)
        if r.status_code != 200:
            r.raise_for_status()  # This will raise an exception for non-200 responses
        g = Graph().parse(data=r.content, format=self.content_type_to_mime_type(
            r.headers['content-type']))
        return [str(o) for (s, o) in g[:URIRef(self.LDP_CONTAINS)]]

    def notification(self, iri, **kwargs):
        """
        Retrieve a single LDN notification and decode into a Python object.
        """
        headers = kwargs.pop("headers", dict())
        if 'accept' not in headers:
            headers['accept'] = kwargs.pop("accept", self.accept_headers)

        r = treq.get(iri, headers=headers, **kwargs)
        if r.status_code != 200:
            r.raise_for_status()  # This will raise an exception for non-200 responses
        mime_type = self.content_type_to_mime_type(r.headers['content-type'])
        if mime_type == self.JSON_LD:
            return r.json()
        else:
            g = Graph().parse(data=r.content, format=mime_type)
            return json.loads(g.serialize(format="json-ld"))
```