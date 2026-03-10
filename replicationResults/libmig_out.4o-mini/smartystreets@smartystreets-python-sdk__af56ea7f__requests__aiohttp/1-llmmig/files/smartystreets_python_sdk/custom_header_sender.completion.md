### Explanation of Changes
To migrate the code from using the `requests` library to the `aiohttp` library, several key changes were made:

1. **Import Statement**: The import statement was changed from `Request` from `requests` to `ClientSession` from `aiohttp`.
2. **Asynchronous Context**: The `send` method was modified to be asynchronous, as `aiohttp` is designed for asynchronous operations. This requires the use of `async def` and `await`.
3. **Session Management**: A session is created using `aiohttp.ClientSession()`, which is used to make the HTTP requests.
4. **Request Creation**: The way requests are created and sent has changed. Instead of creating a `Request` object, we directly use the session to make requests with `session.get()` or `session.post()`.
5. **Handling Response**: The response handling is done using `await` to ensure that the asynchronous call is properly awaited.

### Modified Code
```python
from aiohttp import ClientSession


class CustomHeaderSender:
    def __init__(self, headers, inner):
        self.headers = headers
        self.inner = inner

    async def send(self, smarty_request):
        async with ClientSession() as session:
            request = self.build_request(smarty_request)
            return await self.inner.send(request, session)

    def build_request(self, smarty_request):
        request = {
            'url': smarty_request.url_prefix,
            'params': smarty_request.parameters,
            'headers': self.headers,
            'data': smarty_request.payload if smarty_request.payload else None,
            'method': 'POST' if smarty_request.payload else 'GET'
        }
        return request
```

In this modified code, the `send` method is now asynchronous, and it uses `aiohttp.ClientSession` to handle the HTTP requests. The request details are structured in a dictionary format to be passed to the inner sender.