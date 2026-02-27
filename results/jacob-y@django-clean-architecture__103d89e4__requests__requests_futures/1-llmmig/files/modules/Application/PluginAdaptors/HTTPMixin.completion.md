### Explanation of Changes:
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `requests_futures.sessions` to use the `FuturesSession` class.
2. **Session Initialization**: Created an instance of `FuturesSession` to handle asynchronous requests.
3. **Request Methods**: Updated the `_get` and `_post` methods to use the `FuturesSession` instance for making asynchronous requests (`session.get` and `session.post`).
4. **Response Handling**: Since `requests_futures` returns a `Future` object, the `.result()` method is called to retrieve the actual `Response` object before processing it.
5. **No Other Changes**: The rest of the code remains unchanged to ensure compatibility with the existing application.

### Modified Code:
```python
from requests_futures.sessions import FuturesSession
from requests.exceptions import RequestException
from abc import ABC, abstractmethod


class HTTPMixin(ABC):
    """
    Very basic code used to make HTTP requests.
    """

    def __init__(self):
        # Initialize a FuturesSession for asynchronous requests
        self.session = FuturesSession()

    def send(self) -> dict:
        match self._method():
            case 'GET':
                return self._get()
            case 'POST':
                return self._post()
            case _:
                raise Exception(f'Unsupported HTTP method {self._method()}')

    def _get(self) -> dict:
        # Use FuturesSession to make an asynchronous GET request
        future = self.session.get(self._endpoint(), headers=self._headers(), auth=self._auth())
        response = future.result()  # Wait for the response and retrieve it
        return self._process_response(response)

    def _post(self) -> dict:
        # Use FuturesSession to make an asynchronous POST request
        if self._is_form_encoded():
            headers = self._headers()
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            future = self.session.post(self._endpoint(), data=self._data(), headers=headers, auth=self._auth())
        else:
            future = self.session.post(self._endpoint(), json=self._data(), headers=self._headers(), auth=self._auth())
        response = future.result()  # Wait for the response and retrieve it
        return self._process_response(response)

    @staticmethod
    def _process_response(response) -> dict:
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

### Key Points:
- The `FuturesSession` class from `requests_futures` is used to handle asynchronous HTTP requests.
- The `.result()` method is called on the `Future` object to block until the response is available, ensuring compatibility with the existing synchronous workflow.
- The rest of the code structure, including method names and logic, remains unchanged to avoid breaking the application.