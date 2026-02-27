### Explanation of Changes
To migrate the code from `requests` to `httpx`, the following changes were made:
1. Replaced `requests.Session` with `httpx.Client` for managing sessions.
2. Replaced `requests.Request` with `httpx.Request` for building HTTP requests.
3. Updated the `send` method to use `httpx.Client.send` instead of `requests.Session.send`.
4. Adjusted the `build_request` function to use `httpx.Request` attributes and methods.
5. Updated the `build_proxies` method to match `httpx`'s proxy configuration format.
6. Replaced `requests`-specific methods like `prepare_request` and `merge_environment_settings` with equivalent `httpx` functionality.
7. Updated the `with` block in the `send` method to use `httpx.Response` instead of `requests.Response`.

### Modified Code
```python
from httpx import Client, Request
from .response import Response
import smartystreets_python_sdk as smarty
import smartystreets_python_sdk_version as version


class RequestsSender:
    def __init__(self, max_timeout=None, proxy=None, ip=None):
        self.client = Client()
        self.max_timeout = max_timeout or 10
        self.proxy = proxy
        self.debug = None
        self.ip = ip

    def send(self, smarty_request):
        ip = self.ip
        request = build_request(smarty_request, ip)
        proxies = self.build_proxies()
        if self.debug:
            print_request_data(request)

        with self.client.send(request, timeout=self.max_timeout, proxies=proxies) as response:
            if self.debug:
                print_response_data(response)
            return build_smarty_response(response)

    def build_proxies(self):
        if not self.proxy:
            return None
        if self.proxy.host == 'http://' or self.proxy.host == 'https://':
            raise smarty.exceptions.SmartyException('Proxy must have a valid host (including port)')

        proxy_string = self.proxy.host

        if self.proxy.username:
            proxy_string = '{}:{}@{}'.format(self.proxy.username, self.proxy.password, self.proxy.host)

        if 'https://' in self.proxy.host:
            return {'https': proxy_string}
        else:
            return {'http': proxy_string, 'https': proxy_string}


def build_request(smarty_request, ip=None):
    try:
        method = 'POST' if smarty_request.payload else 'GET'
        headers = {
            'User-Agent': "smartystreets (sdk:python@{})".format(version.__version__),
            'Content-Type': smarty_request.content_type,
        }
        if smarty_request.referer:
            headers['Referer'] = smarty_request.referer
        if ip is not None:
            headers['X-Forwarded-For'] = ip

        request = Request(
            method=method,
            url=smarty_request.url_prefix,
            params=smarty_request.parameters,
            headers=headers,
            content=smarty_request.payload if smarty_request.payload else None,
        )
        return request
    except AttributeError:
        return smarty_request


def build_smarty_response(inner_response, error=None):
    return Response(inner_response.text, inner_response.status_code, inner_response.headers, error)


def print_request_data(request):
    print(request.method)
    print()
    print('URL: {}\r\n'.format(request.url))
    print('Headers:')
    for header, value in request.headers.items():
        print('  {}: {}'.format(header, value))
    print()
    print('Body: ')
    print('  {}\r\n'.format(request.content))


def print_response_data(response):
    print('****** Response ******\r\n')
    print(response.status_code)
    print()
    print(response.text)
    print('**********************\r\n')
```

### Key Notes
- `httpx.Client` is used instead of `requests.Session` for session management.
- `httpx.Request` is used to construct requests, and its attributes like `content` replace `data` from `requests`.
- `httpx.Client.send` is used to send the request, and the `proxies` parameter is passed directly.
- Proxy configuration in `httpx` uses a dictionary format similar to `requests`, but the proxy string format is slightly adjusted.
- The `timeout` parameter in `httpx` is passed directly to the `send` method.
- The `with` block ensures proper handling of the `httpx.Response` object, similar to `requests.Response`.

These changes ensure the code is fully migrated to use `httpx` while maintaining the original functionality and structure.