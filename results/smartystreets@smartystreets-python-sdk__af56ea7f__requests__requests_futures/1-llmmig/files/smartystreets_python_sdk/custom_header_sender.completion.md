### Explanation of Changes:
To migrate from the `requests` library to `requests_futures`, the primary difference is that `requests_futures` provides asynchronous request capabilities by wrapping `requests` with `concurrent.futures`. The `Request` class from `requests` is still compatible with `requests_futures`, so no changes are needed for request creation. However, the `send` method must be updated to use the `FuturesSession` object provided by `requests_futures` for asynchronous execution.

Here are the specific changes made:
1. Imported `FuturesSession` from `requests_futures` instead of using the `Request` class directly from `requests`.
2. Replaced the `inner.send(request)` call with the appropriate `FuturesSession` method to send the request asynchronously.
3. Updated the `CustomHeaderSender` class to initialize and use a `FuturesSession` object for sending requests.

### Modified Code:
```python
from requests_futures.sessions import FuturesSession


class CustomHeaderSender:
    def __init__(self, headers, inner):
        self.headers = headers
        self.inner = FuturesSession()  # Use FuturesSession for asynchronous requests

    def send(self, smarty_request):
        request = self.build_request(smarty_request)
        # Send the request asynchronously using FuturesSession
        if request.method == 'POST':
            return self.inner.post(request.url, headers=request.headers, data=request.data, params=request.params)
        else:  # Default to GET
            return self.inner.get(request.url, headers=request.headers, params=request.params)

    def build_request(self, smarty_request):
        request = Request(url=smarty_request.url_prefix, params=smarty_request.parameters)
        request.headers = self.headers
        if smarty_request.payload:
            request.data = smarty_request.payload
            request.method = 'POST'
        else:
            request.method = 'GET'
        return request
```

### Key Notes:
- The `FuturesSession` object is used to send requests asynchronously.
- The `send` method now explicitly checks the HTTP method (`POST` or `GET`) and uses the corresponding `FuturesSession` method (`post` or `get`).
- The `build_request` method remains unchanged because it is still compatible with `requests_futures`.