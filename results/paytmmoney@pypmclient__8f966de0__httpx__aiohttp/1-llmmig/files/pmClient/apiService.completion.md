### Explanation of Changes
To migrate the code from `httpx` to `aiohttp`, the following changes were made:
1. **Import Changes**: Replaced the `httpx` import with `aiohttp`.
2. **Session Management**: `aiohttp` requires an `aiohttp.ClientSession` for making requests. A session is created and used for all HTTP calls.
3. **Asynchronous Nature**: `aiohttp` is fully asynchronous, so all HTTP calls (`post`, `get`, `put`, `delete`) are now `await`ed. The `api_call_helper` and `_api_call` methods were converted to `async` functions.
4. **Response Handling**: `aiohttp` responses need to be explicitly read using `await response.text()` or `await response.json()`.
5. **Error Handling**: Replaced `httpx.HTTPError` with `aiohttp.ClientError` for raising exceptions.
6. **JSON Data**: `aiohttp` requires the `json` parameter for sending JSON data in requests, instead of manually serializing it with `json.dumps`.

### Modified Code
Here is the updated code using `aiohttp`:

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
        headers = {'Content-Type': "application/json",
                   'openapi-client-src': "sdk"}
        if jwt_token is not None:
            headers['x-jwt-token'] = jwt_token

        async with aiohttp.ClientSession() as session:
            if http_method is Requests.POST:
                async with session.post(url, json=data, headers=headers) as r:
                    return r
            elif http_method is Requests.DELETE:
                async with session.delete(url, headers=headers) as r:
                    return r
            elif http_method is Requests.PUT:
                async with session.put(url, json=data, headers=headers) as r:
                    return r
            elif http_method is Requests.GET:
                async with session.get(url, headers=headers) as r:
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
- The `api_call_helper` and `_api_call` methods are now `async` functions, so they must be called with `await` in the rest of the application.
- The `aiohttp.ClientSession` is used for all HTTP requests, and the session is closed automatically using an `async with` block.
- The `json` parameter in `aiohttp` is used to send JSON data directly, avoiding the need for `json.dumps`.
- Response content is read using `await response.text()` or `await response.json()` depending on the expected format.