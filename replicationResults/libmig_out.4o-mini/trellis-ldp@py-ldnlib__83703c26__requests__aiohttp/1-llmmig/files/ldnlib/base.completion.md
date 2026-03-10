### Explanation of Changes

To migrate the code from using the `requests` library to the `aiohttp` library, several key changes were made:

1. **Importing aiohttp**: The `requests` library was replaced with `aiohttp`, which is designed for asynchronous HTTP requests.
2. **Asynchronous Functions**: The methods that perform HTTP requests (`__discover_head` and `__discover_get`) were converted to asynchronous functions using the `async def` syntax.
3. **Session Management**: An `aiohttp.ClientSession` was created to manage connections, which is necessary for making requests with `aiohttp`.
4. **Awaiting Requests**: The `requests.head` and `requests.get` calls were replaced with their `aiohttp` counterparts (`session.head` and `session.get`), and these calls were awaited.
5. **Handling Responses**: The response handling was adjusted to work with the asynchronous nature of `aiohttp`, including using `await response.text()` to get the response body.

Here is the modified code:

```python
from rdflib import Graph, URIRef
import aiohttp
import asyncio


class BaseLDN(object):

    ACCEPT_HEADERS = ("application/ld+json; q=1.0,"
                      "text/turtle; q=0.9,"
                      "application/xml+rdf; q=0.5")
    JSON_LD = "application/ld+json"
    LDP_INBOX = "http://www.w3.org/ns/ldp#inbox"
    LDP_CONTAINS = "http://www.w3.org/ns/ldp#contains"

    def __init__(self, **kwargs):
        self.accept_headers = kwargs.get('accept_headers', self.ACCEPT_HEADERS)

    async def __discover_head(self, target, **kwargs):
        async with aiohttp.ClientSession() as session:
            async with session.head(target, **kwargs) as r:
                r.raise_for_status()
                if self.LDP_INBOX in r.links:
                    return r.links[self.LDP_INBOX].get('url')

    async def __discover_get(self, target, **kwargs):
        async with aiohttp.ClientSession() as session:
            async with session.get(target, **kwargs) as r:
                r.raise_for_status()
                # TODO -- check for HTML
                g = Graph().parse(data=await r.text(), format=self.content_type_to_mime_type(
                    r.headers['content-type']))

                for (subject, inbox) in g[:URIRef(self.LDP_INBOX)]:
                    return str(inbox)

    def content_type_to_mime_type(self, content_type):
        """
        A utility method to convert a content-type header into a
        mime-type string.
        """
        return content_type.split(";")[0].strip()

    async def discover(self, target, **kwargs):
        """Discover the inbox for a resource."""
        headers = kwargs.pop("headers", dict())
        if 'accept' not in headers:
            headers['accept'] = kwargs.pop("accept", self.accept_headers)
        allow_redirects = kwargs.pop('allow_redirects', True)

        inbox = await self.__discover_head(target, headers=headers,
                                            allow_redirects=allow_redirects,
                                            **kwargs)
        if inbox is None:
            return await self.__discover_get(target, headers=headers,
                                              allow_redirects=allow_redirects,
                                              **kwargs)
        else:
            return inbox
```

### Note
- The `asyncio` library is typically used to run asynchronous code, so you may need to ensure that the calling context of these methods is also asynchronous.