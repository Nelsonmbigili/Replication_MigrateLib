from rdflib import Graph, URIRef
import pycurl
import json
from io import BytesIO

from .base import BaseLDN


class Consumer(BaseLDN):

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

    def notifications(self, inbox, **kwargs):
        """
        Retrieve all of the notification IRIs from an ldp:inbox as a list.
        """
        headers = kwargs.pop("headers", dict())
        if 'accept' not in headers:
            headers['accept'] = kwargs.pop("accept", self.accept_headers)

        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, inbox)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.HTTPHEADER, [f"{key}: {value}" for key, value in headers.items()])
        
        try:
            c.perform()
            response_code = c.getinfo(c.RESPONSE_CODE)
            if response_code != 200:
                raise Exception(f"HTTP error: {response_code}")
        finally:
            c.close()

        body = buffer.getvalue().decode('utf-8')
        g = Graph().parse(data=body, format=self.content_type_to_mime_type(
            c.getinfo(c.CONTENT_TYPE)))
        return [str(o) for (s, o) in g[:URIRef(self.LDP_CONTAINS)]]

    def notification(self, iri, **kwargs):
        """
        Retrieve a single LDN notification and decode into a Python object.
        """
        headers = kwargs.pop("headers", dict())
        if 'accept' not in headers:
            headers['accept'] = kwargs.pop("accept", self.accept_headers)

        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, iri)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.HTTPHEADER, [f"{key}: {value}" for key, value in headers.items()])
        
        try:
            c.perform()
            response_code = c.getinfo(c.RESPONSE_CODE)
            if response_code != 200:
                raise Exception(f"HTTP error: {response_code}")
        finally:
            c.close()

        body = buffer.getvalue().decode('utf-8')
        mime_type = self.content_type_to_mime_type(c.getinfo(c.CONTENT_TYPE))
        if mime_type == self.JSON_LD:
            return json.loads(body)
        else:
            g = Graph().parse(data=body, format=mime_type)
            return json.loads(g.serialize(format="json-ld"))
