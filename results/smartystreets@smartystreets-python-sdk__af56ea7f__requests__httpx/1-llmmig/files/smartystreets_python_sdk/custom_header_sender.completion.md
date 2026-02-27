### Explanation of Changes:
To migrate the code from `requests` to `httpx`, the following changes were made:
1. Replaced the `requests.Request` class with `httpx.Request`.
2. Updated the way the `Request` object is created and configured:
   - In `httpx`, the `Request` constructor directly accepts `method`, `url`, `params`, `headers`, and `data` as arguments. This eliminates the need to set these attributes separately after creating the `Request` object.
3. Adjusted the `send` method to use `httpx.Client` for sending the request, as `httpx` does not have a direct equivalent to `requests.Session.send` for raw `Request` objects. Instead, `httpx.Client` is used to send the request.

### Modified Code:
```python
from httpx import Request, Client


class CustomHeaderSender:
    def __init__(self, headers, inner):
        self.headers = headers
        self.inner = inner

    def send(self, smarty_request):
        request = self.build_request(smarty_request)
        return self.inner.send(request)

    def build_request(self, smarty_request):
        method = 'POST' if smarty_request.payload else 'GET'
        request = Request(
            method=method,
            url=smarty_request.url_prefix,
            params=smarty_request.parameters,
            headers=self.headers,
            data=smarty_request.payload if smarty_request.payload else None
        )
        return request
```

### Key Notes:
- The `httpx.Request` constructor simplifies the process of setting attributes like `method`, `url`, `params`, `headers`, and `data`.
- The `inner.send(request)` assumes that `inner` is an instance of `httpx.Client` or a compatible interface that can send `httpx.Request` objects. If `inner` is not an `httpx.Client`, additional adjustments may be needed to ensure compatibility.