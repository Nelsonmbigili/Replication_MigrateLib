The following Python code currently uses the library "requests" version 2.31.0.
Migrate this code to use the library "httpx" version 0.28.1 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "requests" to "httpx".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "requests" and "httpx".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
import requests
from requests.exceptions import RequestException
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
        return self._process_response(requests.get(self._endpoint(), headers=self._headers(), auth=self._auth()))

    def _post(self) -> dict:
        if self._is_form_encoded():
            headers = self._headers()
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            return self._process_response(
                requests.post(self._endpoint(), data=self._data(), headers=self._headers(), auth=self._auth()))
        return self._process_response(
            requests.post(self._endpoint(), json=self._data(), headers=self._headers(), auth=self._auth()))

    @staticmethod
    def _process_response(response: requests.Response) -> dict:
        try:
            if 200 <= response.status_code < 500:
                return response.json()
            else:
                raise Exception(f"HTTP {response.status_code} error while calling {response.url}")
        except RequestException:
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

```