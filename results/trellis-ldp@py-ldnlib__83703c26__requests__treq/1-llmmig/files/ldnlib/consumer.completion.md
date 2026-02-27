### Explanation of Changes
To migrate the code from using the `requests` library to the `treq` library, the following changes were made:
1. **Asynchronous Nature of `treq`**: `treq` is built on top of `Twisted` and is asynchronous. Therefore, the methods `notifications` and `notification` were converted to `async` functions, and `await` was used for `treq` calls.
2. **Replacing `requests.get`**: The `requests.get` calls were replaced with `treq.get`. The `treq.get` method returns a `Deferred` object, so we used `await` to resolve it and retrieve the response.
3. **Reading Response Content**: In `treq`, the response content is read using `await response.text()` or `await treq.json_content(response)` instead of `r.text` or `r.json()` in `requests`.
4. **Error Handling**: `requests.raise_for_status()` was replaced with a manual check of the response status code (`response.code`) and raising an exception if the status code indicates an error.
5. **Headers and Parameters**: The headers and additional parameters were passed to `treq.get` in the same way as `requests.get`.

### Modified Code
```python
from rdflib import Graph, URIRef
import treq

import json

from .base import BaseLDN


class Consumer(BaseLDN):

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

    async def notifications(self, inbox, **kwargs):
        """
        Retrieve all of the notification IRIs from an ldp:inbox as a list.
        """
        headers = kwargs.pop("headers", dict())
        if 'accept' not in headers:
            headers['accept'] = kwargs.pop("accept", self.accept_headers)

        response = await treq.get(inbox, headers=headers, **kwargs)
        if response.code >= 400:
            raise Exception(f"HTTP Error: {response.code}")

        response_text = await response.text()
        g = Graph().parse(data=response_text, format=self.content_type_to_mime_type(
            response.headers.getRawHeaders('content-type')[0]))
        return [str(o) for (s, o) in g[:URIRef(self.LDP_CONTAINS)]]

    async def notification(self, iri, **kwargs):
        """
        Retrieve a single LDN notification and decode into a Python object.
        """
        headers = kwargs.pop("headers", dict())
        if 'accept' not in headers:
            headers['accept'] = kwargs.pop("accept", self.accept_headers)

        response = await treq.get(iri, headers=headers, **kwargs)
        if response.code >= 400:
            raise Exception(f"HTTP Error: {response.code}")

        mime_type = self.content_type_to_mime_type(
            response.headers.getRawHeaders('content-type')[0])
        response_text = await response.text()

        if mime_type == self.JSON_LD:
            return json.loads(response_text)
        else:
            g = Graph().parse(data=response_text, format=mime_type)
            return json.loads(g.serialize(format="json-ld"))
```

### Key Notes
1. **Asynchronous Code**: Since `treq` is asynchronous, the methods `notifications` and `notification` must be called within an asynchronous context (e.g., using `await` or within an `async` function).
2. **Error Handling**: The `raise_for_status` method from `requests` is not available in `treq`, so we manually check the response status code and raise an exception for HTTP errors.
3. **Headers Handling**: `treq` uses `getRawHeaders` to retrieve headers, which returns a list of values. We use the first value (`[0]`) for processing.

This code maintains the original functionality while adapting to the asynchronous nature of `treq`.