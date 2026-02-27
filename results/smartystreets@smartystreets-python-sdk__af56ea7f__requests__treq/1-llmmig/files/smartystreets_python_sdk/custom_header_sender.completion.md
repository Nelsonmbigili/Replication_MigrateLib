### Explanation of Changes:
To migrate from the `requests` library to the `treq` library, the following changes were made:
1. The `Request` class from `requests` was replaced with the `treq` library's asynchronous HTTP request methods (`treq.get` and `treq.post`).
2. Since `treq` is asynchronous, the `send` method and any other relevant parts of the code were updated to use `async` and `await`.
3. The `build_request` method was removed because `treq` does not use a `Request` object to build requests. Instead, requests are directly made using `treq` methods.
4. The `send` method now directly calls `treq.get` or `treq.post` based on the presence of a payload in `smarty_request`.

### Modified Code:
```python
import treq


class CustomHeaderSender:
    def __init__(self, headers, inner):
        self.headers = headers
        self.inner = inner

    async def send(self, smarty_request):
        if smarty_request.payload:
            # POST request with payload
            response = await treq.post(
                url=smarty_request.url_prefix,
                headers=self.headers,
                params=smarty_request.parameters,
                json=smarty_request.payload
            )
        else:
            # GET request without payload
            response = await treq.get(
                url=smarty_request.url_prefix,
                headers=self.headers,
                params=smarty_request.parameters
            )
        return await self.inner.send(response)
```

### Key Notes:
- The `treq` library is asynchronous, so the `send` method was updated to be an `async` function, and `await` is used to handle asynchronous calls.
- The `build_request` method was removed because `treq` does not require a separate request object to be built. Instead, requests are made directly using `treq.get` or `treq.post`.
- The `params` argument in `treq` is used for query parameters, and the `json` argument is used for the payload in POST requests.
- The `inner.send` method is assumed to handle the `response` object returned by `treq`. If `inner.send` is not asynchronous, further adjustments may be needed.