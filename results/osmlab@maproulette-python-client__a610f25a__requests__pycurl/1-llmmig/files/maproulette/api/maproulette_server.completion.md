### Explanation of Changes:
To migrate the code from the `requests` library to the `pycurl` library, the following changes were made:
1. **Session Management**: `pycurl` does not have a session object like `requests`. Instead, each request is handled individually using a `pycurl.Curl` object. This means that headers, certificates, and other configurations must be set for each request.
2. **Request Methods**: Each HTTP method (`GET`, `POST`, `PUT`, `DELETE`) was rewritten using `pycurl`'s API. The `Curl` object is configured with the appropriate options for each method.
3. **Response Handling**: `pycurl` does not return a response object like `requests`. Instead, the response is written to a buffer, which is then processed to extract the status code, headers, and body.
4. **Error Handling**: `pycurl` raises exceptions for connection errors and other issues. These exceptions were mapped to the custom error classes used in the original code.
5. **Multipart File Uploads**: For the `put_file` method, `pycurl`'s `FORM_FILE` option was used to handle file uploads.
6. **Health Check**: The `__check_health` method was updated to use `pycurl` for the `GET` request.

Below is the modified code:

---

### Modified Code:
```python
"""This module contains the basic methods that handle API calls to the MapRoulette API. It uses the pycurl library to
accomplish this."""

import pycurl
import json
import time
from io import BytesIO
from .errors import HttpError, InvalidJsonError, ConnectionUnavailableError, UnauthorizedError, NotFoundError


class MapRouletteServer:
    """Class that holds the basic requests that can be made to the MapRoulette API."""
    def __init__(self, configuration):
        self.url = configuration.api_url
        self.base_url = configuration.base_url
        self.headers = configuration.headers
        self.certs = configuration.certs
        self.verify = configuration.verify
        if self.__check_health():
            self.session_headers = self.headers

    def __check_health(self, retries=3, delay=5):
        """Checks health of connection to host by pinging the URL set in the configuration

        :param retries: the number of retries to use to successfully ping the URL. Default is 3
        :param delay: the number of seconds to wait between retries
        :returns: True if GET request to ping endpoint is successful
        """
        for i in range(retries):
            try:
                response = self._make_request(
                    method="GET",
                    url=self.base_url + '/ping'
                )
                if response["status"] != 200:
                    print(f"Unsuccessful connection. Retrying in {str(delay)} seconds")
                    time.sleep(delay)
                else:
                    return True
            except ConnectionUnavailableError:
                print(f"Connection not available. Attempt {str(i+1)} out of {str(retries)}")
                time.sleep(delay)

        raise ConnectionUnavailableError(
            message='Specified server unavailable'
        )

    def _make_request(self, method, url, params=None, body=None, files=None):
        """Helper method to make HTTP requests using pycurl."""
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEDATA, buffer)
        curl.setopt(pycurl.HTTPHEADER, [f"{k}: {v}" for k, v in self.session_headers.items()])
        if not self.verify:
            curl.setopt(pycurl.SSL_VERIFYHOST, 0)
            curl.setopt(pycurl.SSL_VERIFYPEER, 0)
        if self.certs:
            curl.setopt(pycurl.SSLCERT, self.certs)

        if method == "GET" and params:
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            curl.setopt(pycurl.URL, f"{url}?{query_string}")
        elif method == "POST":
            curl.setopt(pycurl.POST, 1)
            if body:
                curl.setopt(pycurl.POSTFIELDS, json.dumps(body))
        elif method == "PUT":
            curl.setopt(pycurl.CUSTOMREQUEST, "PUT")
            if body:
                curl.setopt(pycurl.POSTFIELDS, json.dumps(body))
            if files:
                curl.setopt(pycurl.HTTPPOST, [(k, (pycurl.FORM_FILE, v)) for k, v in files.items()])
        elif method == "DELETE":
            curl.setopt(pycurl.CUSTOMREQUEST, "DELETE")

        try:
            curl.perform()
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
            curl.close()
            response_data = buffer.getvalue().decode('utf-8')
            return {
                "data": json.loads(response_data) if self.is_json(response_data) else response_data,
                "status": status_code
            }
        except pycurl.error as e:
            raise ConnectionUnavailableError(message=str(e))
        finally:
            buffer.close()

    def get(self, endpoint, params=None):
        """Method that completes a GET request to the MapRoulette API."""
        response = self._make_request("GET", self.url + endpoint, params=params)
        if response["status"] == 404:
            raise NotFoundError(
                message=self.parse_response_message(response["data"]),
                status=response["status"]
            )
        elif response["status"] >= 400:
            raise HttpError(
                message=self.parse_response_message(response["data"]),
                status=response["status"]
            )
        return response

    def post(self, endpoint, body=None, params=None):
        """Method that completes a POST request to the MapRoulette API."""
        response = self._make_request("POST", self.url + endpoint, params=params, body=body)
        if response["status"] == 400:
            raise InvalidJsonError(
                message=self.parse_response_message(response["data"]),
                status=response["status"]
            )
        elif response["status"] == 401:
            raise UnauthorizedError(
                message=self.parse_response_message(response["data"]),
                status=response["status"]
            )
        elif response["status"] >= 400:
            raise HttpError(
                message=self.parse_response_message(response["data"]),
                status=response["status"]
            )
        return response

    def put(self, endpoint, body=None, params=None):
        """Method that completes a PUT request to the MapRoulette API."""
        response = self._make_request("PUT", self.url + endpoint, params=params, body=body)
        if response["status"] >= 400:
            raise HttpError(
                message=self.parse_response_message(response["data"]),
                status=response["status"]
            )
        return response

    def put_file(self, endpoint, body=None, params=None):
        """Method that completes a multipart PUT request to the MapRoulette API."""
        response = self._make_request("PUT", self.url + endpoint, params=params, files=body)
        if response["status"] >= 400:
            raise HttpError(
                message=self.parse_response_message(response["data"]),
                status=response["status"]
            )
        return response

    def delete(self, endpoint, params=None):
        """Method that completes a DELETE request to the MapRoulette API."""
        response = self._make_request("DELETE", self.url + endpoint, params=params)
        if response["status"] == 401:
            raise UnauthorizedError(
                message=self.parse_response_message(response["data"]),
                status=response["status"]
            )
        elif response["status"] == 404:
            raise NotFoundError(
                message=self.parse_response_message(response["data"]),
                status=response["status"]
            )
        elif response["status"] >= 400:
            raise HttpError(
                message=self.parse_response_message(response["data"]),
                status=response["status"]
            )
        return response

    @staticmethod
    def is_json(input_object):
        """Method to determine whether user input is valid JSON."""
        try:
            json_object = json.loads(input_object)
            del json_object
            return True
        except ValueError:
            return False

    @staticmethod
    def parse_response_message(response):
        """Method to determine the message body from a response object."""
        try:
            return json.loads(response)['message']
        except (ValueError, KeyError):
            return None
```

---

### Key Notes:
- The `pycurl` library requires more manual configuration compared to `requests`.
- The `_make_request` method centralizes the logic for handling different HTTP methods.
- Error handling and response parsing remain consistent with the original code.