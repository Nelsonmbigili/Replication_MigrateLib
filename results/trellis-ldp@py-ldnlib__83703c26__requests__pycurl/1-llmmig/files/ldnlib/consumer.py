from rdflib import Graph, URIRef
import pycurl
from io import BytesIO
import json

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

        # Prepare headers for pycurl
        curl_headers = [f"{key}: {value}" for key, value in headers.items()]

        # Set up pycurl
        c = pycurl.Curl()
        c.setopt(c.URL, inbox)
        c.setopt(c.HTTPHEADER, curl_headers)

        # Capture response body
        response_body = BytesIO()
        c.setopt(c.WRITEDATA, response_body)

        # Perform the request
        c.perform()

        # Check HTTP status code
        status_code = c.getinfo(c.RESPONSE_CODE)
        if status_code < 200 or status_code >= 300:
            c.close()
            raise Exception(f"HTTP request failed with status code {status_code}")

        # Parse response
        response_text = response_body.getvalue().decode('utf-8')
        content_type = c.getinfo(c.CONTENT_TYPE)
        c.close()

        g = Graph().parse(data=response_text, format=self.content_type_to_mime_type(content_type))
        return [str(o) for (s, o) in g[:URIRef(self.LDP_CONTAINS)]]

    def notification(self, iri, **kwargs):
        """
        Retrieve a single LDN notification and decode into a Python object.
        """
        headers = kwargs.pop("headers", dict())
        if 'accept' not in headers:
            headers['accept'] = kwargs.pop("accept", self.accept_headers)

        # Prepare headers for pycurl
        curl_headers = [f"{key}: {value}" for key, value in headers.items()]

        # Set up pycurl
        c = pycurl.Curl()
        c.setopt(c.URL, iri)
        c.setopt(c.HTTPHEADER, curl_headers)

        # Capture response body
        response_body = BytesIO()
        c.setopt(c.WRITEDATA, response_body)

        # Perform the request
        c.perform()

        # Check HTTP status code
        status_code = c.getinfo(c.RESPONSE_CODE)
        if status_code < 200 or status_code >= 300:
            c.close()
            raise Exception(f"HTTP request failed with status code {status_code}")

        # Parse response
        response_text = response_body.getvalue().decode('utf-8')
        content_type = c.getinfo(c.CONTENT_TYPE)
        c.close()

        mime_type = self.content_type_to_mime_type(content_type)
        if mime_type == self.JSON_LD:
            return json.loads(response_text)
        else:
            g = Graph().parse(data=response_text, format=mime_type)
            return json.loads(g.serialize(format="json-ld"))
