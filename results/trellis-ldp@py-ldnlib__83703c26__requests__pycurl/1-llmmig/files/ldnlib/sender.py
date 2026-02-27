from rdflib import Graph
import pycurl
import io
import ipaddress
import json
import socket
from urllib.parse import urlparse

from .base import BaseLDN


class Sender(BaseLDN):

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.allow_localhost = kwargs.get('allow_localhost', False)

    def __accept_post_options(self, inbox, **kwargs):
        headers = {}
        response_buffer = io.BytesIO()

        def header_function(header_line):
            # Parse headers into a dictionary
            if ':' in header_line:
                key, value = header_line.split(':', 1)
                headers[key.strip().lower()] = value.strip()

        c = pycurl.Curl()
        c.setopt(c.URL, inbox)
        c.setopt(c.CUSTOMREQUEST, "OPTIONS")
        c.setopt(c.HEADERFUNCTION, header_function)
        c.setopt(c.WRITEDATA, response_buffer)

        try:
            c.perform()
            status_code = c.getinfo(c.RESPONSE_CODE)
            c.close()

            if status_code == 200 and 'accept-post' in headers:
                if self.JSON_LD in headers['accept-post']:
                    return self.JSON_LD

                for content_type in headers['accept-post'].split(','):
                    return self.content_type_to_mime_type(content_type)
        except pycurl.error as e:
            c.close()
            raise RuntimeError(f"Failed to perform OPTIONS request: {e}")

    def __is_localhost(self, inbox):
        return ipaddress.ip_address(socket.gethostbyname(
            urlparse(inbox).hostname)).is_loopback

    def __post_message(self, inbox, data, content_type, **kwargs):
        if self.allow_localhost or not self.__is_localhost(inbox):
            headers = kwargs.pop("headers", dict())
            headers['Content-Type'] = content_type

            response_buffer = io.BytesIO()
            c = pycurl.Curl()
            c.setopt(c.URL, inbox)
            c.setopt(c.POST, 1)
            c.setopt(c.POSTFIELDS, data)
            c.setopt(c.WRITEDATA, response_buffer)

            # Convert headers dictionary to a list of header strings
            header_list = [f"{key}: {value}" for key, value in headers.items()]
            c.setopt(c.HTTPHEADER, header_list)

            try:
                c.perform()
                status_code = c.getinfo(c.RESPONSE_CODE)
                c.close()

                if status_code >= 400:
                    raise RuntimeError(f"HTTP POST failed with status code {status_code}")
            except pycurl.error as e:
                c.close()
                raise RuntimeError(f"Failed to perform POST request: {e}")
        else:
            raise ValueError("Invalid local inbox.")

    def send(self, inbox, data, **kwargs):
        """Send the provided data to an inbox."""
        if isinstance(data, dict) or isinstance(data, list):
            self.__post_message(inbox, json.dumps(data), self.JSON_LD,
                                **kwargs)
        elif isinstance(data, str):
            self.__post_message(inbox, data, self.JSON_LD, **kwargs)
        elif isinstance(data, Graph):
            ct = self.__accept_post_options(inbox, **kwargs) or self.JSON_LD
            self.__post_message(inbox, data.serialize(format=ct), ct,
                                **kwargs)
        else:
            raise TypeError(
                    "You cannot send data of type {}.".format(type(data)))
