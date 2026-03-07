### Explanation of Changes
To migrate the code from using the `requests` library to the `aiohttp` library, the following changes were made:

1. **Import Statement**: The import statement for `Response` was removed since `aiohttp` does not have a direct equivalent. Instead, we will use `aiohttp.ClientResponse` in the context of the code.
2. **Response Handling**: The methods that handle the response (like `json()` and `text`) will be adapted to work with `aiohttp.ClientResponse`. The `json()` method in `aiohttp` is asynchronous, so it will be awaited.
3. **Error Handling**: The error handling remains similar, but we ensure that the response handling is compatible with `aiohttp`.

The modified code is as follows:

```python
from aiohttp import ClientResponse


class PolyException(Exception):
    def __init__(self, msg):
        self.msg = msg


class PolyApiException(PolyException):
    def __init__(self, resp: ClientResponse = None, error_msg=None):
        assert resp is not None or error_msg is not None
        if resp is not None:
            self.status_code = resp.status
            self.error_msg = self._get_message(resp)
        if error_msg is not None:
            self.error_msg = error_msg
            self.status_code = None

    async def _get_message(self, resp: ClientResponse):
        try:
            return await resp.json()
        except Exception:
            return await resp.text()

    def __repr__(self):
        return "PolyApiException[status_code={}, error_message={}]".format(
            self.status_code, self.error_msg
        )

    def __str__(self):
        return self.__repr__()
```

### Note
- The `_get_message` method is now defined as an asynchronous method (`async def`) to accommodate the `await` keyword for calling `resp.json()` and `resp.text()`. This change assumes that the calling context will handle the asynchronous nature of this method.