from rdflib import Graph, URIRef
import urllib3

import json

from .base import BaseLDN


class Consumer(BaseLDN):

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.http = urllib3.PoolManager()  # Create a PoolManager for HTTP requests

    def notifications(self, inbox, **kwargs):
        """
        Retrieve all of the notification IRIs from an ldp:inbox as a list.
        """
        headers = kwargs.pop("headers", dict())
        if 'accept' not in headers:
            headers['accept'] = kwargs.pop("accept", self.accept_headers)

        # Perform the GET request using urllib3
        response = self.http.request("GET", inbox, headers=headers, **kwargs)
        
        # Raise an error if the status code is not 2xx
        if response.status >= 400:
            raise urllib3.exceptions.HTTPError(f"HTTP request failed with status code {response.status}")

        # Parse the response data
        g = Graph().parse(data=response.data.decode('utf-8'), format=self.content_type_to_mime_type(
            response.headers['content-type']))
        return [str(o) for (s, o) in g[:URIRef(self.LDP_CONTAINS)]]

    def notification(self, iri, **kwargs):
        """
        Retrieve a single LDN notification and decode into a Python object.
        """
        headers = kwargs.pop("headers", dict())
        if 'accept' not in headers:
            headers['accept'] = kwargs.pop("accept", self.accept_headers)

        # Perform the GET request using urllib3
        response = self.http.request("GET", iri, headers=headers, **kwargs)
        
        # Raise an error if the status code is not 2xx
        if response.status >= 400:
            raise urllib3.exceptions.HTTPError(f"HTTP request failed with status code {response.status}")

        # Determine the MIME type and parse the response accordingly
        mime_type = self.content_type_to_mime_type(response.headers['content-type'])
        if mime_type == self.JSON_LD:
            return json.loads(response.data.decode('utf-8'))
        else:
            g = Graph().parse(data=response.data.decode('utf-8'), format=mime_type)
            return json.loads(g.serialize(format="json-ld"))
