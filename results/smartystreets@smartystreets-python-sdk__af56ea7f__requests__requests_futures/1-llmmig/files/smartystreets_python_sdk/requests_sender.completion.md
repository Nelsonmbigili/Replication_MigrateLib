### Explanation of Changes
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Changes**: Replaced the import of `Session` and `Request` from `requests` with `FuturesSession` from `requests_futures`.
2. **Session Replacement**: Replaced the `Session` object with a `FuturesSession` object to enable asynchronous request handling.
3. **Request Sending**: Updated the `send` method to use the asynchronous `send` method provided by `FuturesSession`. The `send` method now waits for the response using `.result()` to maintain compatibility with the synchronous behavior of the original code.
4. **No Other Changes**: The rest of the code remains unchanged to ensure compatibility with the existing application.

### Modified Code
```python
from requests_futures.sessions import FuturesSession
from requests import Request
from .response import Response
import smartystreets_python_sdk as smarty
import smartystreets_python_sdk_version as version


class RequestsSender:
    def __init__(self, max_timeout=None, proxy=None, ip=None):
        self.session = FuturesSession()
        self.max_timeout = max_timeout or 10
        self.proxy = proxy
        self.debug = None
        self.ip = ip

    def send(self, smarty_request):
        ip = self.ip
        request = build_request(smarty_request, ip)
        prepped_request = self.session.prepare_request(request)
        prepped_proxies = self.build_proxies()
        if self.debug:
            print_request_data(prepped_request)

        settings = self.session.merge_environment_settings(
            prepped_request.url, prepped_proxies, None, None, None
        )
        # Send the request asynchronously and wait for the result
        future_response = self.session.send(prepped_request, timeout=self.max_timeout, **settings)
        response = future_response.result()  # Wait for the response to complete
        if self.debug:
            print_response_data(response)
        return build_smarty_response(response)

    def build_proxies(self):
        if not self.proxy:
            return {}
        if (self.proxy.host == 'http://' or self.proxy.host == 'https://'):
            raise smarty.exceptions.SmartyException('Proxy must have a valid host (including port)')

        proxy_string = self.proxy.host

        if self.proxy.username:
            proxy_string += '{}:{}@'.format(self.proxy.username, self.proxy.password)

        if ('https://' in self.proxy.host):
            return {'https': proxy_string}
        else:
            return {'http': proxy_string, 'https': proxy_string}


def build_request(smarty_request, ip=None):
    try:
        request = Request(url=smarty_request.url_prefix, params=smarty_request.parameters)
        request.headers['User-Agent'] = "smartystreets (sdk:python@{})".format(version.__version__)
        request.headers['Content-Type'] = smarty_request.content_type
        if smarty_request.referer:
            request.headers['Referer'] = smarty_request.referer
        if ip != None:
            request.headers['X-Forwarded-For'] = ip
        if smarty_request.payload:
            request.data = smarty_request.payload
            request.method = 'POST'
        else:
            request.method = 'GET'
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
    for header in request.headers:
        print('  {}: {}'.format(header, request.headers[header]))
    print()
    print('Body: ')
    print('  {}\r\n'.format(request.body))


def print_response_data(response):
    print('****** Response ******\r\n')
    print(response.status_code)
    print()
    print(response.text)
    print('**********************\r\n')
```

### Summary of Changes
- Replaced `Session` with `FuturesSession` to enable asynchronous requests.
- Used `.result()` to wait for the asynchronous response, preserving the synchronous behavior of the original code.
- No other changes were made to the structure, logic, or style of the code.