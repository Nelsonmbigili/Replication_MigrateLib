### Explanation of Changes
To migrate the code from using the `httpx` library to the `aiohttp` library, the following changes were made:

1. **Import Statement**: Changed the import from `httpx` to `aiohttp`.
2. **Asynchronous Context**: Since `aiohttp` is designed for asynchronous operations, the `_api_call` method was modified to be asynchronous. This required adding `async` to the method definition and using `await` for the HTTP calls.
3. **Response Handling**: The response handling was updated to use `await response.json()` for JSON responses and `await response.text()` for text responses.
4. **Session Management**: An `aiohttp.ClientSession` was introduced to manage connections, which is necessary for making requests with `aiohttp`.

### Modified Code
```python
import aiohttp
import json
from .enums import Requests
from .constants import Constants

class ApiService(Constants):
    def __init__(self):
        Constants.__init__(self)

    async def api_call_helper(self, name, http_method, params, data):
        """helper formats the url and reads error codes nicely"""
        config = self._service_config
        url = f"{config['host']}{config['routes'][name][0]}"
        if params is not None:
            url = url.format(**params)
        jwt_token = self.validate_token(config, name)
        response = await self._api_call(url, http_method, jwt_token, data)
        if response.status != 200:
            if response.status == 400:
                raise AttributeError(await response.text())
            elif response.status == 404:
                raise Exception(await response.text())
            elif response.status == 415:
                raise Exception(await response.text())
            elif response.status == 500:
                raise Exception(await response.text())
            elif response.status == 401:
                raise ConnectionError(await response.text())
            else:
                raise aiohttp.ClientError(await response.text(), response.status)
        if not url.find('security_master') == -1:
            return await response.text()
        else:
            return await response.json()

    async def _api_call(self, url, http_method, jwt_token, data):
        """Checks for the API Method and that call is done and returned"""
        headers = {'Content-Type' : "application/json",
                   'openapi-client-src' : "sdk"}
        if jwt_token is not None:
            headers['x-jwt-token'] = jwt_token
        async with aiohttp.ClientSession() as session:
            r = None
            if http_method is Requests.POST:
                r = await session.post(url, json=data, headers=headers)
            elif http_method is Requests.DELETE:
                r = await session.delete(url, headers=headers)
            elif http_method is Requests.PUT:
                r = await session.put(url, json=data, headers=headers)
            elif http_method is Requests.GET:
                r = await session.get(url, headers=headers)
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

This modified code now uses `aiohttp` for asynchronous HTTP requests while maintaining the original structure and logic of the code.