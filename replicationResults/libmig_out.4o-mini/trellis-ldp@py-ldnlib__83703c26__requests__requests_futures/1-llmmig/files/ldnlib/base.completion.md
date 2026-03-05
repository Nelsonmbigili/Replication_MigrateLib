### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Import Statement**: The import statement for `requests` was replaced with `requests_futures.sessions` to utilize the `FuturesSession` class, which allows for asynchronous requests.
2. **Session Initialization**: Instead of directly using `requests.head` and `requests.get`, a `FuturesSession` object was created to handle the requests asynchronously.
3. **Handling Responses**: The responses from the asynchronous requests are handled using the `result()` method to retrieve the actual response object.

Here is the modified code:

```python
from rdflib import Graph, URIRef
from requests_futures.sessions import FuturesSession


class BaseLDN(object):

    ACCEPT_HEADERS = ("application/ld+json; q=1.0,"
                      "text/turtle; q=0.9,"
                      "application/xml+rdf; q=0.5")
    JSON_LD = "application/ld+json"
    LDP_INBOX = "http://www.w3.org/ns/ldp#inbox"
    LDP_CONTAINS = "http://www.w3.org/ns/ldp#contains"

    def __init__(self, **kwargs):
        self.accept_headers = kwargs.get('accept_headers', self.ACCEPT_HEADERS)
        self.session = FuturesSession()  # Initialize FuturesSession

    def __discover_head(self, target, **kwargs):
        future = self.session.head(target, **kwargs)  # Use FuturesSession
        r = future.result()  # Get the response
        r.raise_for_status()
        if self.LDP_INBOX in r.links:
            return r.links[self.LDP_INBOX].get('url')

    def __discover_get(self, target, **kwargs):
        future = self.session.get(target, **kwargs)  # Use FuturesSession
        r = future.result()  # Get the response
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

This code now uses `requests_futures` to perform asynchronous HTTP requests while maintaining the original structure and functionality.