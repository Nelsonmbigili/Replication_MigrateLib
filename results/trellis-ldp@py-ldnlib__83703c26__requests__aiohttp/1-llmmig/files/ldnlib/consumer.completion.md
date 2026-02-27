### Explanation of Changes
To migrate the code from `requests` to `aiohttp`, the following changes were made:
1. **Asynchronous Programming**: `aiohttp` is an asynchronous library, so the methods `notifications` and `notification` were converted to asynchronous functions using the `async def` syntax.
2. **Session Management**: `aiohttp` requires an `aiohttp.ClientSession` for making HTTP requests. A session is created and used for the `GET` requests.
3. **Awaiting Requests**: Since `aiohttp` uses coroutines, the `get` method and other asynchronous operations are awaited using the `await` keyword.
4. **Response Handling**: The response content is accessed using `await response.text()` for text data and `await response.json()` for JSON data.
5. **Error Handling**: `aiohttp` does not have a `raise_for_status` method like `requests`. Instead, the status code is checked manually, and an exception is raised if the status code indicates an error.

### Modified Code
Here is the complete code after migrating to `aiohttp`:

```python
from rdflib import Graph, URIRef
import aiohttp
import asyncio
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

        async with aiohttp.ClientSession() as session:
            async with session.get(inbox, headers=headers, **kwargs) as response:
                if response.status != 200:
                    response_text = await response.text()
                    raise aiohttp.ClientResponseError(
                        status=response.status,
                        message=f"Error: {response_text}"
                    )
                response_text = await response.text()
                g = Graph().parse(data=response_text, format=self.content_type_to_mime_type(
                    response.headers['content-type']))
                return [str(o) for (s, o) in g[:URIRef(self.LDP_CONTAINS)]]

    async def notification(self, iri, **kwargs):
        """
        Retrieve a single LDN notification and decode into a Python object.
        """
        headers = kwargs.pop("headers", dict())
        if 'accept' not in headers:
            headers['accept'] = kwargs.pop("accept", self.accept_headers)

        async with aiohttp.ClientSession() as session:
            async with session.get(iri, headers=headers, **kwargs) as response:
                if response.status != 200:
                    response_text = await response.text()
                    raise aiohttp.ClientResponseError(
                        status=response.status,
                        message=f"Error: {response_text}"
                    )
                mime_type = self.content_type_to_mime_type(response.headers['content-type'])
                if mime_type == self.JSON_LD:
                    return await response.json()
                else:
                    response_text = await response.text()
                    g = Graph().parse(data=response_text, format=mime_type)
                    return json.loads(g.serialize(format="json-ld"))
```

### Key Points
- The `notifications` and `notification` methods are now asynchronous (`async def`).
- `aiohttp.ClientSession` is used for making HTTP requests, and the session is properly closed using an `async with` block.
- The `await` keyword is used to handle asynchronous operations like `session.get`, `response.text()`, and `response.json()`.
- Error handling is implemented by checking the `response.status` and raising an `aiohttp.ClientResponseError` if the status code is not 200.

This code is now fully migrated to use `aiohttp` while maintaining the original functionality and structure.