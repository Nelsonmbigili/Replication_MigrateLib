### Explanation of Changes
To migrate the code from `httpx` to `urllib3`, the following changes were made:
1. **Import Changes**: Removed the `httpx` import and replaced it with `urllib3`.
2. **HTTP Client Setup**: `urllib3` requires creating an `urllib3.PoolManager` instance to manage HTTP connections. This replaces the direct `httpx` function calls.
3. **HTTP Requests**: Replaced `httpx` methods (`httpx.get`, `httpx.post`, etc.) with `urllib3.PoolManager` methods (`manager.request`).
   - `urllib3` uses a unified `request` method for all HTTP methods, so the HTTP method is passed as a string.
   - The `data` parameter in `urllib3` requires a byte string, so `json.dumps(data)` is encoded using `.encode('utf-8')`.
4. **Response Handling**: `urllib3` responses are handled differently:
   - Access the response body using `response.data.decode('utf-8')` instead of `response.text`.
   - `urllib3` does not raise exceptions for HTTP status codes, so custom error handling was added to raise exceptions based on `response.status`.
5. **Error Handling**: Replaced `httpx.HTTPError` with a generic `Exception` since `urllib3` does not have a specific HTTP error class.

### Modified Code
```python
import urllib3
import json
from .enums import Requests
from .constants import Constants

class ApiService(Constants):
    def __init__(self):
        Constants.__init__(self)
        self.manager = urllib3.PoolManager()  # Create a PoolManager instance for HTTP requests

    def api_call_helper(self, name, http_method, params, data):
        """helper formats the url and reads error codes nicely"""
        config = self._service_config
        url = f"{config['host']}{config['routes'][name][0]}"
        if params is not None:
            url = url.format(**params)
        jwt_token = self.validate_token(config, name)
        response = self._api_call(url, http_method, jwt_token, data)
        if response.status != 200:  # urllib3 uses `status` instead of `status_code`
            if response.status == 400:
                raise AttributeError(response.data.decode('utf-8'))
            elif response.status == 404:
                raise Exception(response.data.decode('utf-8'))
            elif response.status == 415:
                raise Exception(response.data.decode('utf-8'))
            elif response.status == 500:
                raise Exception(response.data.decode('utf-8'))
            elif response.status == 401:
                raise ConnectionError(response.data.decode('utf-8'))
            else:
                raise Exception(response.data.decode('utf-8'))  # Generic exception for other status codes
        if not url.find('security_master') == -1:
            return response.data.decode('utf-8')  # Decode response data to string
        else:
            return json.loads(response.data.decode('utf-8'))  # Decode and parse JSON response

    def _api_call(self, url, http_method, jwt_token, data):
        """Checks for the API Method and that call is done and returned"""
        headers = {'Content-Type': "application/json",
                   'openapi-client-src': "sdk"}
        if jwt_token is not None:
            headers['x-jwt-token'] = jwt_token
        r = None
        if http_method is Requests.POST:
            r = self.manager.request(
                "POST", url, body=json.dumps(data).encode('utf-8'), headers=headers
            )
        elif http_method is Requests.DELETE:
            r = self.manager.request("DELETE", url, headers=headers)
        elif http_method is Requests.PUT:
            r = self.manager.request(
                "PUT", url, body=json.dumps(data).encode('utf-8'), headers=headers
            )
        elif http_method is Requests.GET:
            r = self.manager.request("GET", url, headers=headers)
        return r

    def validate_token(self, config, name):
        """
        Validate jwt tokens 
        """
        tokens = (config['routes'][name][1])
        jwt_token = None
        if self.access_token is not None and "access_token" in tokens:
            jwt_token = self.access_token
        if self.public_access_token is not None and "public_access_token" in tokens:
            jwt_token = self.public_access_token
        if self.read_access_token is not None and "read_access_token" in tokens:
            jwt_token = self.read_access_token
        if len(tokens) > 0 and jwt_token is None:
            raise TypeError("Token is invalid: " + ' or '.join(tokens))
        else:
            return jwt_token
```

### Key Notes
- The `urllib3.PoolManager` instance (`self.manager`) is used to manage all HTTP requests.
- The `data` parameter for `POST` and `PUT` requests is encoded to bytes using `.encode('utf-8')`.
- Response data is decoded using `.decode('utf-8')` to convert it back to a string.
- Error handling was adjusted to work with `urllib3`'s response object, which uses `status` instead of `status_code`.