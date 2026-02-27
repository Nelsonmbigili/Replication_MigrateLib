import pycurl
import io
import json
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
            return self._process_response(self._make_request('POST', form_encoded=True))
        return self._process_response(self._make_request('POST', form_encoded=False))

    def _make_request(self, method: str, form_encoded: bool = False) -> tuple:
        """
        Makes an HTTP request using pycurl and returns the response body and status code.
        """
        curl = pycurl.Curl()
        buffer = io.BytesIO()

        try:
            # Set the URL
            curl.setopt(pycurl.URL, self._endpoint())

            # Set headers
            headers = [f"{key}: {value}" for key, value in self._headers().items()]
            curl.setopt(pycurl.HTTPHEADER, headers)

            # Set authentication if provided
            if self._auth():
                curl.setopt(pycurl.USERPWD, f"{self._auth()[0]}:{self._auth()[1]}")

            # Configure method-specific options
            if method == 'POST':
                curl.setopt(pycurl.POST, 1)
                if form_encoded:
                    curl.setopt(pycurl.POSTFIELDS, self._data())  # Form-encoded data
                else:
                    curl.setopt(pycurl.POSTFIELDS, json.dumps(self._data()))  # JSON data

            # Write response to buffer
            curl.setopt(pycurl.WRITEFUNCTION, buffer.write)

            # Perform the request
            curl.perform()

            # Get the response status code
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)

        except pycurl.error as e:
            raise Exception(f"Connection failed while calling {self._endpoint()}: {e}")
        finally:
            curl.close()

        # Return the response body and status code
        return buffer.getvalue(), status_code

    @staticmethod
    def _process_response(response: tuple) -> dict:
        """
        Processes the response from pycurl.
        """
        body, status_code = response
        try:
            body = body.decode('utf-8')  # Decode bytes to string
            if 200 <= status_code < 500:
                return json.loads(body)  # Parse JSON response
            else:
                raise Exception(f"HTTP {status_code} error while calling the endpoint")
        except json.JSONDecodeError:
            raise Exception("Failed to parse JSON response")
        except Exception as e:
            raise Exception(str(e))

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
