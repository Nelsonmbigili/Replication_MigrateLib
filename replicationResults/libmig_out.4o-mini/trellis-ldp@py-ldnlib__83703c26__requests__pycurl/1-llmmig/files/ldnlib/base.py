from rdflib import Graph, URIRef
import pycurl
from io import BytesIO


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
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, target)
        c.setopt(c.NOBODY, True)
        headers = kwargs.get('headers', {})
        if 'accept' in headers:
            headers_list = [f'Accept: {headers["accept"]}']
        else:
            headers_list = [f'Accept: {self.accept_headers}']
        c.setopt(c.HTTPHEADER, headers_list)
        c.setopt(c.WRITEFUNCTION, buffer.write)
        c.perform()
        response_code = c.getinfo(c.RESPONSE_CODE)
        c.close()

        if response_code != 200:
            raise Exception(f"HTTP error: {response_code}")

        # Check for LDP_INBOX in headers (not directly available in pycurl)
        # This part may need to be adjusted based on actual response handling
        # For now, we assume we have a way to check for links in headers
        # This is a placeholder for actual link extraction logic
        if self.LDP_INBOX in headers:  # Placeholder logic
            return headers[self.LDP_INBOX]

    def __discover_get(self, target, **kwargs):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, target)
        headers = kwargs.get('headers', {})
        if 'accept' in headers:
            headers_list = [f'Accept: {headers["accept"]}']
        else:
            headers_list = [f'Accept: {self.accept_headers}']
        c.setopt(c.HTTPHEADER, headers_list)
        c.setopt(c.WRITEFUNCTION, buffer.write)
        c.perform()
        response_code = c.getinfo(c.RESPONSE_CODE)
        c.close()

        if response_code != 200:
            raise Exception(f"HTTP error: {response_code}")

        data = buffer.getvalue().decode('utf-8')
        g = Graph().parse(data=data, format=self.content_type_to_mime_type(
            headers.get('content-type', '')))

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
