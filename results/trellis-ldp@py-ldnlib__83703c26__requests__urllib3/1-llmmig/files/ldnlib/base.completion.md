### Explanation of Changes:
To migrate the code from the `requests` library to `urllib3`, the following changes were made:
1. **Replaced `requests.head` with `urllib3.PoolManager`'s `request` method**:
   - `requests.head` was replaced with `urllib3.PoolManager().request('HEAD', ...)`.
   - The `links` attribute of the `requests` response was manually parsed using the `Link` header, as `urllib3` does not provide a `links` attribute.

2. **Replaced `requests.get` with `urllib3.PoolManager`'s `request` method**:
   - `requests.get` was replaced with `urllib3.PoolManager().request('GET', ...)`.
   - The response body (`r.text`) was accessed using `r.data.decode('utf-8')` since `urllib3` returns the response body as bytes.

3. **Error Handling**:
   - `requests.raise_for_status()` was replaced with manual status code checks (`if r.status >= 400: raise ...`).

4. **Headers and Redirects**:
   - Headers and redirect handling were passed directly to `urllib3.PoolManager().request`.

5. **Initialization of `urllib3.PoolManager`**:
   - A `PoolManager` instance was created and reused for all HTTP requests.

### Modified Code:
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
        self.http = urllib3.PoolManager()  # Initialize PoolManager

    def __discover_head(self, target, **kwargs):
        headers = kwargs.get('headers', {})
        allow_redirects = kwargs.get('allow_redirects', True)
        r = self.http.request('HEAD', target, headers=headers, redirect=allow_redirects)
        if r.status >= 400:
            raise urllib3.exceptions.HTTPError(f"HTTP error: {r.status}")

        # Parse the Link header manually
        link_header = r.headers.get('Link', '')
        links = self.parse_link_header(link_header)
        if self.LDP_INBOX in links:
            return links[self.LDP_INBOX]

    def __discover_get(self, target, **kwargs):
        headers = kwargs.get('headers', {})
        allow_redirects = kwargs.get('allow_redirects', True)
        r = self.http.request('GET', target, headers=headers, redirect=allow_redirects)
        if r.status >= 400:
            raise urllib3.exceptions.HTTPError(f"HTTP error: {r.status}")

        # Parse the response body
        g = Graph().parse(data=r.data.decode('utf-8'), format=self.content_type_to_mime_type(
            r.headers['Content-Type']))

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

    @staticmethod
    def parse_link_header(link_header):
        """
        Parse the Link header into a dictionary of rel -> URL.
        """
        links = {}
        if link_header:
            parts = link_header.split(',')
            for part in parts:
                section = part.split(';')
                if len(section) < 2:
                    continue
                url = section[0].strip('<> ')
                rel = None
                for attr in section[1:]:
                    if 'rel=' in attr:
                        rel = attr.split('=')[1].strip('" ')
                if rel:
                    links[rel] = url
        return links
```

### Key Notes:
- The `parse_link_header` method was added to manually parse the `Link` header, as `urllib3` does not provide a `links` attribute like `requests`.
- The `urllib3.PoolManager` instance is reused for all requests to improve performance.
- The response body is decoded using `r.data.decode('utf-8')` since `urllib3` returns the body as bytes.