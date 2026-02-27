from rdflib import Graph, URIRef
import treq

import json

from .base import BaseLDN


class Consumer(BaseLDN):

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

    async def notifications(self, inbox, **kwargs):
        """
        Retrieve all of the notification IRIs from an ldp:inbox as a list.
        """
        headers = kwargs.pop("headers", dict())
        if 'accept' not in headers:
            headers['accept'] = kwargs.pop("accept", self.accept_headers)

        response = await treq.get(inbox, headers=headers, **kwargs)
        if response.code >= 400:
            raise Exception(f"HTTP Error: {response.code}")

        response_text = await response.text()
        g = Graph().parse(data=response_text, format=self.content_type_to_mime_type(
            response.headers.getRawHeaders('content-type')[0]))
        return [str(o) for (s, o) in g[:URIRef(self.LDP_CONTAINS)]]

    async def notification(self, iri, **kwargs):
        """
        Retrieve a single LDN notification and decode into a Python object.
        """
        headers = kwargs.pop("headers", dict())
        if 'accept' not in headers:
            headers['accept'] = kwargs.pop("accept", self.accept_headers)

        response = await treq.get(iri, headers=headers, **kwargs)
        if response.code >= 400:
            raise Exception(f"HTTP Error: {response.code}")

        mime_type = self.content_type_to_mime_type(
            response.headers.getRawHeaders('content-type')[0])
        response_text = await response.text()

        if mime_type == self.JSON_LD:
            return json.loads(response_text)
        else:
            g = Graph().parse(data=response_text, format=mime_type)
            return json.loads(g.serialize(format="json-ld"))
