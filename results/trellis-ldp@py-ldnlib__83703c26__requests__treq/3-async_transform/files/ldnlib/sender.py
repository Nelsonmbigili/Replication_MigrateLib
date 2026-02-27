from rdflib import Graph
import treq

import ipaddress
import json
import socket
from urllib.parse import urlparse

from .base import BaseLDN


class Sender(BaseLDN):

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.allow_localhost = kwargs.get('allow_localhost', False)

    async def __accept_post_options(self, inbox, **kwargs):
        response = await treq.options(inbox, **kwargs)
        if response.code == 200:  # Equivalent to requests.codes.ok
            headers = await response.headers()
            if 'accept-post' in headers:
                if self.JSON_LD in headers['accept-post']:
                    return self.JSON_LD

                for content_type in headers['accept-post'].split(','):
                    return self.content_type_to_mime_type(content_type)

    def __is_localhost(self, inbox):
        return ipaddress.ip_address(socket.gethostbyname(
            urlparse(inbox).hostname)).is_loopback

    async def __post_message(self, inbox, data, content_type, **kwargs):
        if self.allow_localhost or not self.__is_localhost(inbox):
            headers = kwargs.pop("headers", dict())
            headers['content-type'] = content_type
            response = await treq.post(inbox, data=data, headers=headers, **kwargs)
            if response.code >= 400:
                body = await response.text()
                raise Exception(f"HTTP Error {response.code}: {body}")
        else:
            raise ValueError("Invalid local inbox.")

    async def send(self, inbox, data, **kwargs):
        """Send the provided data to an inbox."""
        if isinstance(data, dict) or isinstance(data, list):
            await self.__post_message(inbox, json.dumps(data), self.JSON_LD,
                                      **kwargs)
        elif isinstance(data, str):
            await self.__post_message(inbox, data, self.JSON_LD, **kwargs)
        elif isinstance(data, Graph):
            ct = await self.__accept_post_options(inbox, **kwargs) or self.JSON_LD
            await self.__post_message(inbox, data.serialize(format=ct), ct,
                                      **kwargs)
        else:
            raise TypeError(
                    "You cannot send data of type {}.".format(type(data)))
