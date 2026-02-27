from rdflib import Graph, URIRef
import treq
from twisted.web.http_headers import Headers


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
        response = await treq.head(target, **kwargs)
        if response.code >= 400:
            response.raise_for_status()

        # Parse the Link header manually
        link_header = response.headers.getRawHeaders('Link', [])
        for link in link_header:
            parts = link.split(";")
            url = parts[0].strip("<>")
            rel = None
            for part in parts[1:]:
                if part.strip().startswith("rel="):
                    rel = part.split("=")[1].strip("\"")
            if rel == self.LDP_INBOX:
                return url

    async def __discover_get(self, target, **kwargs):
        response = await treq.get(target, **kwargs)
        if response.code >= 400:
            response.raise_for_status()

        # Parse the response body
        response_text = await response.text()
        g = Graph().parse(data=response_text, format=self.content_type_to_mime_type(
            response.headers.getRawHeaders('Content-Type', [])[0]))

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

        # Convert headers to Twisted Headers object
        twisted_headers = Headers({k: [v] for k, v in headers.items()})

        inbox = await self.__discover_head(target, headers=twisted_headers,
                                           allow_redirects=allow_redirects,
                                           **kwargs)
        if inbox is None:
            return await self.__discover_get(target, headers=twisted_headers,
                                             allow_redirects=allow_redirects,
                                             **kwargs)
        else:
            return inbox
