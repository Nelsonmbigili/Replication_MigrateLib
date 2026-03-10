from rdflib import Graph, URIRef
import aiohttp
import json
import asyncio

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

        async with aiohttp.ClientSession() as session:
            async with session.get(inbox, headers=headers, **kwargs) as r:
                if r.status != 200:
                    r.raise_for_status()
                g = Graph().parse(data=await r.text(), format=self.content_type_to_mime_type(
                    r.headers['content-type']))
                return [str(o) for (s, o) in g[:URIRef(self.LDP_CONTAINS)]]

    async def notification(self, iri, **kwargs):
        """
        Retrieve a single LDN notification and decode into a Python object.
        """
        headers = kwargs.pop("headers", dict())
        if 'accept' not in headers:
            headers['accept'] = kwargs.pop("accept", self.accept_headers)

        async with aiohttp.ClientSession() as session:
            async with session.get(iri, headers=headers, **kwargs) as r:
                if r.status != 200:
                    r.raise_for_status()
                mime_type = self.content_type_to_mime_type(r.headers['content-type'])
                if mime_type == self.JSON_LD:
                    return await r.json()
                else:
                    g = Graph().parse(data=await r.text(), format=mime_type)
                    return json.loads(g.serialize(format="json-ld"))
