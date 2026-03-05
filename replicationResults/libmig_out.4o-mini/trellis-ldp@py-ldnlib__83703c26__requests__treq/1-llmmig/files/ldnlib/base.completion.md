### Explanation of Changes

To migrate the code from using the `requests` library to the `treq` library, the following changes were made:

1. **Import Statement**: The import statement for `requests` was replaced with `treq`.
2. **Method Calls**: The `requests.head()` and `requests.get()` method calls were replaced with `treq.head()` and `treq.get()`, respectively.
3. **Response Handling**: The way to access the response headers and links was adjusted to fit the `treq` library's response object. Specifically, `r.links` was replaced with `r.headers.get('Link')`, and the parsing of the `Link` header was adjusted accordingly.

Here is the modified code:

```python
from rdflib import Graph, URIRef
import treq


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
        r = treq.head(target, **kwargs)
        r.raise_for_status()
        link_header = r.headers.get('Link', '')
        if self.LDP_INBOX in link_header:
            # Extract the URL from the Link header
            links = link_header.split(',')
            for link in links:
                if self.LDP_INBOX in link:
                    return link.split(';')[0].strip('<>')

    def __discover_get(self, target, **kwargs):
        r = treq.get(target, **kwargs)
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

This code now uses `treq` for HTTP requests while maintaining the original structure and functionality of the application.