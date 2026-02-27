import urllib3
from urllib3.exceptions import HTTPError
from abc import ABC, abstractmethod


class HTTPMixin(ABC):
    """
    Very basic code used to make HTTP requests.
    """

    def __init__(self):
        self._http = urllib3.PoolManager()

    def send(self) -> dict:
        match self._method():
            case 'GET':
                return self._get()
            case 'POST':
                return self._post()
            case _:
                raise Exception(f'Unsupported HTTP method {self._method()}')

    def _get(self) -> dict:
        try:
            response = self._http.request(
                'GET',
                self._endpoint(),
                headers=self._headers(),
                auth=self._auth()  # Note: urllib3 does not natively support `auth`, so this may need manual handling.
            )
            return self._process_response(response)
        except HTTPError as e:
            raise Exception(f"Connection failed while calling {self._endpoint()}") from e

    def _post(self) -> dict:
        try:
            headers = self._headers()
            if self._is_form_encoded():
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
                response = self._http.request(
                    'POST',
                    self._endpoint(),
                    body=urllib3.request.urlencode(self._data()),
                    headers=headers,
                    auth=self._auth()  # Note: urllib3 does not natively support `auth`, so this may need manual handling.
                )
            else:
                response = self._http.request(
                    'POST',
                    self._endpoint(),
                    body=json.dumps(self._data()),
                    headers=headers,
                    auth=self._auth()  # Note: urllib3 does not natively support `auth`, so this may need manual handling.
                )
            return self._process_response(response)
        except HTTPError as e:
            raise Exception(f"Connection failed while calling {self._endpoint()}") from e

    @staticmethod
    def _process_response(response: urllib3.response.HTTPResponse) -> dict:
        try:
            if 200 <= response.status < 500:
                return json.loads(response.data.decode('utf-8'))
            else:
                raise Exception(f"HTTP {response.status} error while calling {response.geturl()}")
        except HTTPError:
            raise Exception(f"Connection failed while calling {response.geturl()}")

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
