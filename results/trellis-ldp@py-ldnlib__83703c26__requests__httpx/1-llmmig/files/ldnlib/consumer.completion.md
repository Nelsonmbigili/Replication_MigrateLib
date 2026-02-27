### Explanation of Changes
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `httpx`.
2. **HTTP Methods**: Replaced `requests.get` with `httpx.get`. The method signatures are similar, so no additional changes were needed for arguments like `headers` and `**kwargs`.
3. **Response Handling**: The `httpx` response object is similar to `requests`, so attributes like `text`, `headers`, `json()`, and `raise_for_status()` remain unchanged.
4. **No Other Changes**: The rest of the code remains the same, as the migration only involves replacing the HTTP client library.

### Modified Code
Here is the complete code after migration:

```python
from rdflib import Graph, URIRef
import httpx

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

        r = httpx.get(inbox, headers=headers, **kwargs)
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

        r = httpx.get(iri, headers=headers, **kwargs)
        r.raise_for_status()
        mime_type = self.content_type_to_mime_type(r.headers['content-type'])
        if mime_type == self.JSON_LD:
            return r.json()
        else:
            g = Graph().parse(data=r.text, format=mime_type)
            return json.loads(g.serialize(format="json-ld"))
```

### Summary
The migration from `requests` to `httpx` was straightforward because both libraries have similar APIs for basic HTTP operations. The changes were limited to replacing `requests` with `httpx` in the import statement and method calls. No other modifications were made to the code.