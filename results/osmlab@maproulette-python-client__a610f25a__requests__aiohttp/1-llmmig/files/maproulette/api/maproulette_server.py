"""This module contains the basic methods that handle API calls to the MapRoulette API. It uses the aiohttp library to
accomplish this."""

import aiohttp
import asyncio
import json
import time
from .errors import HttpError, InvalidJsonError, ConnectionUnavailableError, UnauthorizedError, NotFoundError


class MapRouletteServer:
    """Class that holds the basic requests that can be made to the MapRoulette API."""
    def __init__(self, configuration):
        self.url = configuration.api_url
        self.base_url = configuration.base_url
        self.headers = configuration.headers
        self.certs = configuration.certs
        self.verify = configuration.verify
        self.session = None

    async def initialize_session(self):
        """Initializes the aiohttp session asynchronously."""
        if await self.__check_health():
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                connector=aiohttp.TCPConnector(ssl=self.verify),
                json_serialize=json.dumps
            )

    async def __check_health(self, retries=3, delay=5):
        """Checks health of connection to host by pinging the URL set in the configuration

        :param retries: the number of retries to use to successfully ping the URL. Default is 3
        :param delay: the number of seconds to wait between retries
        :returns: True if GET request to ping endpoint is successful
        """
        for i in range(retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        self.base_url + '/ping',
                        ssl=self.verify,
                        headers=self.headers
                    ) as response:
                        if response.status != 200:
                            print(f"Unsuccessful connection. Retrying in {str(delay)} seconds")
                            await asyncio.sleep(delay)
                        else:
                            return True
            except aiohttp.ClientError:
                print(f"Connection not available. Attempt {str(i+1)} out of {str(retries)}")
                await asyncio.sleep(delay)

        raise ConnectionUnavailableError(
            message='Specified server unavailable'
        )

    async def get(self, endpoint, params=None):
        """Method that completes a GET request to the MapRoulette API"""
        async with self.session.get(self.url + endpoint, params=params) as response:
            return await self.__handle_response(response)

    async def post(self, endpoint, body=None, params=None):
        """Method that completes a POST request to the MapRoulette API"""
        async with self.session.post(self.url + endpoint, params=params, json=body) as response:
            return await self.__handle_response(response)

    async def put(self, endpoint, body=None, params=None):
        """Method that completes a PUT request to the MapRoulette API"""
        async with self.session.put(self.url + endpoint, params=params, json=body) as response:
            return await self.__handle_response(response)

    async def put_file(self, endpoint, body=None, params=None):
        """Method that completes a multipart PUT request to the MapRoulette API"""
        async with self.session.put(self.url + endpoint, params=params, data=body) as response:
            return await self.__handle_response(response)

    async def delete(self, endpoint, params=None):
        """Method that completes a DELETE request to the MapRoulette API"""
        async with self.session.delete(self.url + endpoint, params=params) as response:
            return await self.__handle_response(response)

    async def __handle_response(self, response):
        """Handles the response from an aiohttp request."""
        try:
            response.raise_for_status()
        except aiohttp.ClientResponseError as e:
            if e.status == 404:
                raise NotFoundError(
                    message=await self.parse_response_message(response),
                    status=e.status
                ) from None
            elif e.status == 400:
                raise InvalidJsonError(
                    message=await self.parse_response_message(response),
                    status=e.status
                ) from None
            elif e.status == 401:
                raise UnauthorizedError(
                    message=await self.parse_response_message(response),
                    status=e.status
                ) from None
            else:
                raise HttpError(
                    message=await self.parse_response_message(response),
                    status=e.status
                ) from None
        try:
            return {
                "data": await response.json(),
                "status": response.status
            }
        except ValueError:
            return {
                "data": await response.text(),
                "status": response.status
            }

    @staticmethod
    async def parse_response_message(response):
        """Method to determine the message body from a response object. Will return None if message cannot be parsed."""
        try:
            return (await response.json())['message']
        except (ValueError, KeyError):
            return None

    @staticmethod
    def is_json(input_object):
        """Method to determine whether user input is valid JSON."""
        try:
            json_object = json.loads(input_object)
            del json_object
            return True
        except ValueError:
            return False
