import httpx
from httpx import HTTPStatusError
from abc import ABC, abstractmethod


class HTTPMixin(ABC):
    """
    Very basic code used to make HTTP requests.
    """

    def send(self) -> dict:
        match self._method():
            case 'GET':
                return self._get()
            case 'POST':
                return self._post()
            case _:
                raise Exception(f'Unsupported HTTP method {self._method()}')

    def _get(self) -> dict:
        return self._process_response(httpx.get(self._endpoint(), headers=self._headers(), auth=self._auth()))

    def _post(self) -> dict:
        if self._is_form_encoded():
            headers = self._headers()
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            return self._process_response(
                httpx.post(self._endpoint(), data=self._data(), headers=self._headers(), auth=self._auth()))
        return self._process_response(
            httpx.post(self._endpoint(), json=self._data(), headers=self._headers(), auth=self._auth()))

    @staticmethod
    def _process_response(response: httpx.Response) -> dict:
        try:
            response.raise_for_status()  # Raises an HTTPStatusError for bad responses
            return response.json()
        except HTTPStatusError:
            raise Exception(f"HTTP {response.status_code} error while calling {response.url}")
        except Exception:
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
