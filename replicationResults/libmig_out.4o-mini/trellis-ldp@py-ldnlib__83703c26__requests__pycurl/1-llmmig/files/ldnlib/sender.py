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
        buffer = io.BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, inbox)
        c.setopt(c.CUSTOMREQUEST, 'OPTIONS')
        c.setopt(c.WRITEFUNCTION, buffer.write)
        
        if 'headers' in kwargs:
            headers = kwargs['headers']
            c.setopt(c.HTTPHEADER, headers)

        c.perform()
        response_code = c.getinfo(c.RESPONSE_CODE)
        response_data = buffer.getvalue().decode('utf-8')
        c.close()

        if response_code == 200 and 'accept-post' in response_data:
            if self.JSON_LD in response_data:
                return self.JSON_LD

            for content_type in response_data.split(','):
                return self.content_type_to_mime_type(content_type)

    def __is_localhost(self, inbox):
        return ipaddress.ip_address(socket.gethostbyname(
            urlparse(inbox).hostname)).is_loopback

    def __post_message(self, inbox, data, content_type, **kwargs):
        if self.allow_localhost or not self.__is_localhost(inbox):
            buffer = io.BytesIO()
            c = pycurl.Curl()
            c.setopt(c.URL, inbox)
            c.setopt(c.POSTFIELDS, data)
            headers = kwargs.pop("headers", dict())
            headers['content-type'] = content_type
            c.setopt(c.HTTPHEADER, [f"{key}: {value}" for key, value in headers.items()])

            c.perform()
            response_code = c.getinfo(c.RESPONSE_CODE)
            if response_code != 200:
                raise ValueError(f"Request failed with status code {response_code}")
            c.close()
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
