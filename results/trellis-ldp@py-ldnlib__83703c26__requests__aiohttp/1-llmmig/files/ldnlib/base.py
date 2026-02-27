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
