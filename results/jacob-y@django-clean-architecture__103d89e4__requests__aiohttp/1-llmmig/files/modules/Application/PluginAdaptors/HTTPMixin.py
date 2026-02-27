import aiohttp
from aiohttp import ClientError
from abc import ABC, abstractmethod


class HTTPMixin(ABC):
    """
    Very basic code used to make HTTP requests.
    """

    async def send(self) -> dict:
        match self._method():
            case 'GET':
                return await self._get()
            case 'POST':
                return await self._post()
            case _:
                raise Exception(f'Unsupported HTTP method {self._method()}')

    async def _get(self) -> dict:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self._endpoint(), headers=self._headers(), auth=self._auth()) as response:
                    return await self._process_response(response)
            except ClientError as e:
                raise Exception(f"Connection failed while calling {self._endpoint()}") from e

    async def _post(self) -> dict:
        async with aiohttp.ClientSession() as session:
            try:
                if self._is_form_encoded():
                    headers = self._headers()
                    headers['Content-Type'] = 'application/x-www-form-urlencoded'
                    async with session.post(self._endpoint(), data=self._data(), headers=headers, auth=self._auth()) as response:
                        return await self._process_response(response)
                else:
                    async with session.post(self._endpoint(), json=self._data(), headers=self._headers(), auth=self._auth()) as response:
                        return await self._process_response(response)
            except ClientError as e:
                raise Exception(f"Connection failed while calling {self._endpoint()}") from e

    @staticmethod
    async def _process_response(response: aiohttp.ClientResponse) -> dict:
        try:
            if 200 <= response.status < 500:
                return await response.json()
            else:
                raise Exception(f"HTTP {response.status} error while calling {response.url}")
        except ClientError:
            raise Exception(f"Connection failed while calling {response.url}")

    @abstractmethod
    def _method(self) -> str:
        pass

    @abstractmethod
    def _endpoint(self) -> str:
        pass

    @abstractmethod
    def _auth(self) -> tuple | None:
        pass

    @abstractmethod
    def _headers(self) -> dict:
        pass

    @abstractmethod
    def _data(self) -> dict:
        pass

    @abstractmethod
    def _is_form_encoded(self) -> bool:
        pass
