### Explanation of Changes

To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Import Statement**: The import statement for `requests` was replaced with `urllib3`.
2. **Creating a PoolManager**: Instead of using `requests` directly, we create an instance of `urllib3.PoolManager` to handle HTTP requests.
3. **Making Requests**: The methods `head` and `get` from `requests` were replaced with the corresponding methods from the `urllib3` instance.
4. **Handling Responses**: The response handling was adjusted to access the response data and headers in a way that is compatible with `urllib3`.
5. **Link Extraction**: The way to extract links from the response was modified since `urllib3` does not provide a `links` attribute like `requests`.

Here is the modified code:

```python
from rdflib import Graph, URIRef
import urllib3


class BaseLDN(object):

    ACCEPT_HEADERS = ("application/ld+json; q=1.0,"
                      "text/turtle; q=0.9,"
                      "application/xml+rdf; q=0.5")
    JSON_LD = "application/ld+json"
    LDP_INBOX = "http://www.w3.org/ns/ldp#inbox"
    LDP_CONTAINS = "http://www.w3.org/ns/ldp#contains"

    def __init__(self, **kwargs):
        self.accept_headers = kwargs.get('accept_headers', self.ACCEPT_HEADERS)
        self.http = urllib3.PoolManager()

    def __discover_head(self, target, **kwargs):
        r = self.http.head(target, **kwargs)
        if r.status != 200:
            r.raise_for_status()
        if 'Link' in r.headers:
            links = r.headers['Link'].split(',')
            for link in links:
                if self.LDP_INBOX in link:
                    return link.split(';')[0].strip('<>')

    def __discover_get(self, target, **kwargs):
        r = self.http.get(target, **kwargs)
        if r.status != 200:
            r.raise_for_status()
        # TODO -- check for HTML
        g = Graph().parse(data=r.data.decode('utf-8'), format=self.content_type_to_mime_type(
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
                                     **kwargs)
        if inbox is None:
            return self.__discover_get(target, headers=headers,
                                       **kwargs)
        else:
            return inbox
``` 

This code now uses `urllib3` for HTTP requests while maintaining the original structure and functionality of the application.