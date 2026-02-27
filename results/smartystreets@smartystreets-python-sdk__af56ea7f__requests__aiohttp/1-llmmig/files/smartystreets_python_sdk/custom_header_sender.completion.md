### Explanation of Changes:
To migrate the code from `requests` to `aiohttp`, the following changes were made:
1. **Asynchronous Nature**: `aiohttp` is an asynchronous library, so the `send` method and any related calls need to be converted to asynchronous functions using `async def` and `await`.
2. **Request Object**: `aiohttp` does not have a `Request` class like `requests`. Instead, HTTP requests are made using `aiohttp.ClientSession` and its methods (`get`, `post`, etc.).
3. **Headers and Payload**: Headers and payload are passed directly to the `ClientSession` methods.
4. **HTTP Methods**: The HTTP method (`GET` or `POST`) is determined by calling the appropriate method on the `ClientSession` object.

Below is the modified code:

---

### Modified Code:
```python
import aiohttp


class CustomHeaderSender:
    def __init__(self, headers, inner):
        self.headers = headers
        self.inner = inner

    async def send(self, smarty_request):
        request = await self.build_request(smarty_request)
        return await self.inner.send(request)

    async def build_request(self, smarty_request):
        async with aiohttp.ClientSession() as session:
            if smarty_request.payload:
                # POST request
                async with session.post(
                    url=smarty_request.url_prefix,
                    params=smarty_request.parameters,
                    headers=self.headers,
                    data=smarty_request.payload
                ) as response:
                    return response
            else:
                # GET request
                async with session.get(
                    url=smarty_request.url_prefix,
                    params=smarty_request.parameters,
                    headers=self.headers
                ) as response:
                    return response
```

---

### Key Points:
1. The `send` method is now asynchronous (`async def`) and uses `await` to handle asynchronous calls.
2. The `build_request` method creates and sends the HTTP request directly using `aiohttp.ClientSession` instead of building a `Request` object.
3. The `ClientSession` methods (`post` and `get`) are used to handle `POST` and `GET` requests, respectively.
4. The `aiohttp.ClientSession` is used within an `async with` block to ensure proper cleanup of resources.

This code maintains the original structure and logic while adapting it to use `aiohttp`.