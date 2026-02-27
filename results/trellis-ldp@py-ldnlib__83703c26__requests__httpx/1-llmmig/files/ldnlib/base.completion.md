### Explanation of Changes
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:
1. **Import Change**: Replaced `import requests` with `import httpx`.
2. **HTTP Methods**: Updated `requests.head` and `requests.get` to `httpx.head` and `httpx.get`, respectively.
3. **Response Handling**: The `httpx` library uses the same `raise_for_status()` method as `requests`, so no changes were needed there.
4. **Links Attribute**: The `httpx` response object does not have a `links` attribute like `requests`. Instead, we manually parse the `Link` header using `httpx`'s `headers` dictionary.
5. **Headers Handling**: The `httpx` library uses the same approach for headers, so no changes were needed there.
6. **Keyword Arguments**: The `httpx` library supports the same keyword arguments (`headers`, `allow_redirects`, etc.), so no changes were needed for those.

### Modified Code
Here is the complete code after migrating to `httpx`:

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
        # Parse the 'Link' header manually since httpx does not have a 'links' attribute
        link_header = r.headers.get('link', '')
        links = self.parse_link_header(link_header)
        if self.LDP_INBOX in links:
            return links[self.LDP_INBOX]

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

    def parse_link_header(self, link_header):
        """
        Parse the 'Link' header into a dictionary of rel -> url.
        """
        links = {}
        if link_header:
            parts = link_header.split(",")
            for part in parts:
                section = part.split(";")
                if len(section) > 1:
                    url = section[0].strip(" <>")
                    rel = None
                    for attr in section[1:]:
                        if "rel=" in attr:
                            rel = attr.split("=")[1].strip('"')
                    if rel:
                        links[rel] = url
        return links

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

### Key Additions
- **`parse_link_header` Method**: Since `httpx` does not provide a `links` attribute like `requests`, I added a utility method to parse the `Link` header manually. This method extracts the `rel` and `url` values from the `Link` header and returns them as a dictionary.

This ensures the functionality remains consistent with the original `requests`-based implementation.