import pycurl
from io import BytesIO
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
        return self._process_response(self._make_request('GET'))

    def _post(self) -> dict:
        if self._is_form_encoded():
            headers = self._headers()
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            return self._process_response(self._make_request('POST', data=self._data(), headers=headers))
        return self._process_response(self._make_request('POST', json=self._data(), headers=self._headers()))

    def _make_request(self, method: str, data=None, headers=None) -> str:
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, self._endpoint())
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.HTTPHEADER, [f"{key}: {value}" for key, value in (headers or {}).items()])
        if self._auth():
            c.setopt(c.USERPWD, f"{self._auth()[0]}:{self._auth()[1]}")
        if method == 'POST':
            c.setopt(c.POSTFIELDS, data if data else '')
        c.perform()
        c.close()
        return buffer.getvalue().decode('utf-8')

    @staticmethod
    def _process_response(response: str) -> dict:
        try:
            # Assuming the response is JSON
            return json.loads(response)
        except ValueError:
            raise Exception(f"Invalid JSON response")

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
