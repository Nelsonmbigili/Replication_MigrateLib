### Explanation of Changes
To migrate the code from `requests` to `aiohttp`, the following changes were made:
1. **Asynchronous Programming**: `aiohttp` is an asynchronous library, so the methods that use `aiohttp` need to be converted to `async` functions. This includes adding the `async` keyword to the function definitions and using `await` for asynchronous calls.
2. **Session Management**: `aiohttp` requires an `aiohttp.ClientSession` to make HTTP requests. A session is created and used for `head` and `get` requests.
3. **Request Methods**: The `requests.head` and `requests.get` methods are replaced with `session.head` and `session.get` from `aiohttp`.
4. **Error Handling**: `aiohttp` raises exceptions for HTTP errors, so `raise_for_status()` is replaced with a `try-except` block to catch `aiohttp.ClientResponseError`.
5. **Response Handling**: The response content is accessed using `await response.text()` for the body and `response.headers` for headers.
6. **Links Parsing**: `aiohttp` does not have a built-in `links` attribute like `requests`. Instead, the `Link` header is manually parsed if needed.

Below is the modified code.

---

### Modified Code
```python
from rdflib import Graph, URIRef
import aiohttp


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
            try:
                async with session.head(target, **kwargs) as response:
                    response.raise_for_status()
                    # Manually parse the Link header
                    link_header = response.headers.get('Link', '')
                    links = self.parse_link_header(link_header)
                    if self.LDP_INBOX in links:
                        return links[self.LDP_INBOX]
            except aiohttp.ClientResponseError as e:
                raise e

    async def __discover_get(self, target, **kwargs):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(target, **kwargs) as response:
                    response.raise_for_status()
                    # Parse the response content
                    content_type = self.content_type_to_mime_type(
                        response.headers['content-type']
                    )
                    g = Graph().parse(data=await response.text(), format=content_type)

                    for (subject, inbox) in g[:URIRef(self.LDP_INBOX)]:
                        return str(inbox)
            except aiohttp.ClientResponseError as e:
                raise e

    def content_type_to_mime_type(self, content_type):
        """
        A utility method to convert a content-type header into a
        mime-type string.
        """
        return content_type.split(";")[0].strip()

    def parse_link_header(self, link_header):
        """
        Parse the Link header into a dictionary of rel -> url.
        """
        links = {}
        if link_header:
            parts = link_header.split(",")
            for part in parts:
                section = part.split(";")
                url = section[0].strip(" <>")
                rel = None
                for param in section[1:]:
                    if "rel=" in param:
                        rel = param.split("=")[1].strip('"')
                if rel:
                    links[rel] = url
        return links

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

---

### Key Notes
1. **Asynchronous Usage**: The `discover` method and its helper methods (`__discover_head` and `__discover_get`) are now `async`. This means that any code calling `discover` must also use `await`.
2. **Link Header Parsing**: Since `aiohttp` does not provide a `links` attribute, a helper method `parse_link_header` was added to parse the `Link` header manually.
3. **Session Management**: Each HTTP request is wrapped in an `aiohttp.ClientSession` context manager to ensure proper cleanup of resources.

This code is now fully migrated to use `aiohttp` while maintaining the original functionality.