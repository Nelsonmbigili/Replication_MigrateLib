### Explanation of Changes

To migrate the code from using the `httpx` library to the `urllib3` library, the following changes were made:

1. **Import Statement**: The import statement for `httpx` was removed and replaced with an import for `urllib3`. Additionally, `json` remains imported as it is still needed for JSON handling.
  
2. **Creating a Pool Manager**: `urllib3` requires a `PoolManager` to handle connections. This was instantiated in the `ApiService` class.

3. **Making HTTP Requests**: The methods for making HTTP requests (like `post`, `get`, `put`, and `delete`) were changed from `httpx` methods to `urllib3` methods. The `data` parameter in the requests was converted to bytes, as `urllib3` expects the body to be in bytes.

4. **Response Handling**: The response handling was adjusted to work with `urllib3`'s response object, which does not have a `status_code` attribute but instead uses `status` and `data` attributes.

5. **Error Handling**: The error handling was modified to raise exceptions based on the status code from the `urllib3` response.

Here is the modified code:

```python
import urllib3
import json
from .enums import Requests
from .constants import Constants

class ApiService(Constants):
    def __init__(self):
        Constants.__init__(self)
        self.http = urllib3.PoolManager()

    def api_call_helper(self, name, http_method, params, data):
        """helper formats the url and reads error codes nicely"""
        config = self._service_config
        url = f"{config['host']}{config['routes'][name][0]}"
        if params is not None:
            url = url.format(**params)
        jwt_token = self.validate_token(config, name)
        response = self._api_call(url, http_method, jwt_token, data)
        if response.status != 200:
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
                raise Exception(response.data.decode('utf-8'), response.status)
        if not url.find('security_master') == -1:
            return response.data.decode('utf-8')
        else:
            return json.loads(response.data.decode('utf-8'))

    def _api_call(self, url, http_method, jwt_token, data):
        """Checks for the API Method and that call is done and returned"""
        headers = {'Content-Type' : "application/json",
                   'openapi-client-src' : "sdk"}
        if jwt_token is not None:
            headers['x-jwt-token'] = jwt_token
        r = None
        if http_method is Requests.POST:
            r = self.http.request('POST', url, body=json.dumps(data).encode('utf-8'), headers=headers)
        elif http_method is Requests.DELETE:
            r = self.http.request('DELETE', url, headers=headers)
        elif http_method is Requests.PUT:
            r = self.http.request('PUT', url, body=json.dumps(data).encode('utf-8'), headers=headers)
        elif http_method is Requests.GET:
            r = self.http.request('GET', url, headers=headers)
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
        if len(tokens)>0 and jwt_token is None:
            raise TypeError("Token is invalid: "+' or '.join(tokens))
        else:
            return jwt_token
```