import treq
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
        response = await treq.get(self._endpoint(), headers=self._headers(), auth=self._auth())
        return await self._process_response(response)

    async def _post(self) -> dict:
        if self._is_form_encoded():
            headers = self._headers()
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            response = await treq.post(self._endpoint(), data=self._data(), headers=headers, auth=self._auth())
        else:
            response = await treq.post(self._endpoint(), json=self._data(), headers=self._headers(), auth=self._auth())
        return await self._process_response(response)

    @staticmethod
    async def _process_response(response) -> dict:
        try:
            if 200 <= response.code < 500:  # `treq` uses `response.code` instead of `response.status_code`
                return await treq.json_content(response)
            else:
                raise Exception(f"HTTP {response.code} error while calling {response.request.absoluteURI}")
        except Exception as e:
            raise Exception(f"Connection failed while calling {response.request.absoluteURI}") from e

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
