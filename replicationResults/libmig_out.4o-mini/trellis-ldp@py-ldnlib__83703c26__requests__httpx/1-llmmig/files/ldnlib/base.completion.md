### Explanation of Changes

To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:

1. **Import Statement**: Changed the import from `requests` to `httpx`.
2. **Method Calls**: Updated the method calls from `requests.head` and `requests.get` to `httpx.head` and `httpx.get`, respectively.
3. **Response Handling**: The `httpx` library uses a slightly different approach for handling responses. The `links` attribute is accessed in the same way, but the `raise_for_status()` method is called directly on the response object.
4. **Text Access**: The response text is accessed in the same way using `r.text`.

The overall structure and logic of the code remain unchanged, adhering to the requirement of not altering the original coding style or functionality.

### Modified Code

```python
from rdflib import Graph, URIRef
import httpx


class BaseLDN(object):

    ACCEPT_HEADERS = ("application/ld+json; q=1.0,"
                      "text/turtle; q=0.9,"
                      "application/xml+rdf; q=0.5")
    JSON_LD = "application/ld+json"
    LDP_INBOX = "http://www.w3.org/ns/ldp#inbox"
    LDP_CONTAINS = "http://www.w3.org/ns/ldp#contains"

    def __init__(self, **kwargs):
        self.accept_headers = kwargs.get('accept_headers', self.ACCEPT_HEADERS)

    def __discover_head(self, target, **kwargs):
        r = httpx.head(target, **kwargs)
        r.raise_for_status()
        if self.LDP_INBOX in r.links:
            return r.links[self.LDP_INBOX].get('url')

    def __discover_get(self, target, **kwargs):
        r = httpx.get(target, **kwargs)
        r.raise_for_status()
        # TODO -- check for HTML
        g = Graph().parse(data=r.text, format=self.content_type_to_mime_type(
            r.headers['content-type']))

        for (subject, inbox) in g[:URIRef(self.LDP_INBOX)]:
            return str(inbox)

    def content_type_to_mime_type(self, content_type):
        """
        A utility method to convert a content-type header into a
        mime-type string.
        """
        return content_type.split(";")[0].strip()

    def discover(self, target, **kwargs):
        """Discover the inbox for a resource."""
        headers = kwargs.pop("headers", dict())
        if 'accept' not in headers:
            headers['accept'] = kwargs.pop("accept", self.accept_headers)
        allow_redirects = kwargs.pop('allow_redirects', True)

        inbox = self.__discover_head(target, headers=headers,
                                     allow_redirects=allow_redirects,
                                     **kwargs)
        if inbox is None:
            return self.__discover_get(target, headers=headers,
                                       allow_redirects=allow_redirects,
                                       **kwargs)
        else:
            return inbox
```