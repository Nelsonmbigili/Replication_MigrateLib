### Explanation of Changes

To migrate the code from using the `requests` library to the `treq` library, the following changes were made:

1. **Session Management**: `treq` does not use a `Session` object like `requests`. Instead, it uses `treq`'s functions directly for making HTTP requests. The `Session` object and its associated methods were removed.
   
2. **Request Preparation**: `treq` does not have a `prepare_request` method. Instead, the request is directly constructed and sent using `treq`'s `get`, `post`, or other HTTP methods. The `build_request` function was modified to return the necessary parameters for `treq`'s methods.

3. **Sending Requests**: The `send` method was updated to use `treq`'s asynchronous request methods (`treq.get`, `treq.post`, etc.) instead of `session.send`. Since `treq` is asynchronous, the `send` method was converted to an `async` function, and `await` was used to handle the asynchronous calls.

4. **Timeouts**: `treq` supports timeouts via the `timeout` parameter in its request methods. This was directly passed to the `treq` request.

5. **Proxies**: `treq` supports proxies via the `proxy` parameter. The `build_proxies` method was updated to return a `proxy` string compatible with `treq`.

6. **Response Handling**: `treq` returns a `Response` object that must be awaited to access its content. The `build_smarty_response` function was updated to handle this.

7. **Debugging**: The `print_request_data` and `print_response_data` functions were updated to work with `treq`'s request and response objects.

---

### Modified Code

```python
import treq
from .response import Response
import smartystreets_python_sdk as smarty
import smartystreets_python_sdk_version as version


class RequestsSender:
    def __init__(self, max_timeout=None, proxy=None, ip=None):
        self.max_timeout = max_timeout or 10
        self.proxy = proxy
        self.debug = None
        self.ip = ip

    async def send(self, smarty_request):
        ip = self.ip
        url, method, headers, params, data = build_request(smarty_request, ip)
        proxy = self.build_proxies()

        if self.debug:
            print_request_data(method, url, headers, params, data)

        response = await treq.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            timeout=self.max_timeout,
            proxy=proxy,
        )

        if self.debug:
            await print_response_data(response)

        return await build_smarty_response(response)

    def build_proxies(self):
        if not self.proxy:
            return None
        if self.proxy.host == 'http://' or self.proxy.host == 'https://':
            raise smarty.exceptions.SmartyException('Proxy must have a valid host (including port)')

        proxy_string = self.proxy.host

        if self.proxy.username:
            proxy_string = '{}:{}@{}'.format(self.proxy.username, self.proxy.password, self.proxy.host)

        return proxy_string


def build_request(smarty_request, ip=None):
    try:
        url = smarty_request.url_prefix
        params = smarty_request.parameters
        headers = {
            'User-Agent': "smartystreets (sdk:python@{})".format(version.__version__),
            'Content-Type': smarty_request.content_type,
        }
        if smarty_request.referer:
            headers['Referer'] = smarty_request.referer
        if ip is not None:
            headers['X-Forwarded-For'] = ip

        data = smarty_request.payload if smarty_request.payload else None
        method = 'POST' if smarty_request.payload else 'GET'

        return url, method, headers, params, data
    except AttributeError:
        return smarty_request


async def build_smarty_response(inner_response, error=None):
    text = await inner_response.text()
    return Response(text, inner_response.code, inner_response.headers, error)


def print_request_data(method, url, headers, params, data):
    print(method)
    print()
    print('URL: {}\r\n'.format(url))
    print('Headers:')
    for header in headers:
        print('  {}: {}'.format(header, headers[header]))
    print()
    print('Params: ')
    print('  {}\r\n'.format(params))
    print('Body: ')
    print('  {}\r\n'.format(data))


async def print_response_data(response):
    print('****** Response ******\r\n')
    print(response.code)
    print()
    print(await response.text())
    print('**********************\r\n')
```

---

### Key Notes:
1. The `send` method is now asynchronous (`async def`) because `treq` is an asynchronous library.
2. All calls to `treq` methods (e.g., `treq.request`, `response.text`) are awaited.
3. The `build_request` function now returns the necessary components (`url`, `method`, `headers`, `params`, `data`) for `treq`'s request methods.
4. The `build_proxies` method returns a proxy string compatible with `treq`.
5. Debugging functions (`print_request_data` and `print_response_data`) were updated to handle `treq`'s request and response objects.