### Explanation of Changes
To migrate the code from the `requests` library to `urllib3`, the following changes were made:
1. **Session Replacement**: The `requests.Session` object was replaced with `urllib3.PoolManager`, which is the equivalent in `urllib3` for managing connections.
2. **Request Preparation**: The `requests.Request` and `session.prepare_request` methods were replaced with direct handling of HTTP requests using `urllib3.PoolManager.request`.
3. **Timeouts and Proxies**: The `urllib3` library handles timeouts and proxies differently. The `timeout` parameter was passed directly to the `request` method, and proxies were configured using the `proxy_url` parameter in `PoolManager`.
4. **Headers and Data**: The `urllib3` library requires headers and data to be passed directly to the `request` method.
5. **Response Handling**: The `urllib3` response object (`HTTPResponse`) was used to extract the response body, status code, and headers.
6. **Error Handling**: Adjustments were made to handle potential differences in exceptions between `requests` and `urllib3`.

Below is the modified code.

---

### Modified Code
```python
from urllib3 import PoolManager
from urllib3.exceptions import HTTPError
from .response import Response
import smartystreets_python_sdk as smarty
import smartystreets_python_sdk_version as version


class RequestsSender:
    def __init__(self, max_timeout=None, proxy=None, ip=None):
        self.session = PoolManager()
        self.max_timeout = max_timeout or 10
        self.proxy = proxy
        self.debug = None
        self.ip = ip

    def send(self, smarty_request):
        ip = self.ip
        request_data = build_request(smarty_request, ip)
        url = request_data['url']
        method = request_data['method']
        headers = request_data['headers']
        body = request_data.get('body', None)
        proxies = self.build_proxies()

        if self.debug:
            print_request_data(request_data)

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                body=body,
                timeout=self.max_timeout,
                proxy_url=proxies.get('https') if 'https' in proxies else None
            )
            if self.debug:
                print_response_data(response)
            return build_smarty_response(response)
        except HTTPError as e:
            return build_smarty_response(None, error=str(e))

    def build_proxies(self):
        if not self.proxy:
            return {}
        if (self.proxy.host == 'http://' or self.proxy.host == 'https://'):
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
        url = smarty_request.url_prefix
        headers = {
            'User-Agent': "smartystreets (sdk:python@{})".format(version.__version__),
            'Content-Type': smarty_request.content_type
        }
        if smarty_request.referer:
            headers['Referer'] = smarty_request.referer
        if ip is not None:
            headers['X-Forwarded-For'] = ip

        method = 'POST' if smarty_request.payload else 'GET'
        body = smarty_request.payload if smarty_request.payload else None

        return {
            'url': url,
            'method': method,
            'headers': headers,
            'body': body
        }
    except AttributeError:
        return smarty_request


def build_smarty_response(inner_response, error=None):
    if inner_response is None:
        return Response(None, 0, {}, error)
    return Response(
        inner_response.data.decode('utf-8'),
        inner_response.status,
        inner_response.headers,
        error
    )


def print_request_data(request):
    print(request['method'])
    print()
    print('URL: {}\r\n'.format(request['url']))
    print('Headers:')
    for header in request['headers']:
        print('  {}: {}'.format(header, request['headers'][header]))
    print()
    print('Body: ')
    print('  {}\r\n'.format(request.get('body', '')))


def print_response_data(response):
    print('****** Response ******\r\n')
    print(response.status)
    print()
    print(response.data.decode('utf-8'))
    print('**********************\r\n')
```

---

### Key Notes
1. **Proxy Handling**: `urllib3` uses the `proxy_url` parameter in `PoolManager.request` for proxy configuration. This was adapted in the `build_proxies` method.
2. **Error Handling**: The `HTTPError` exception from `urllib3` was used to handle request errors.
3. **Response Decoding**: The `urllib3` response body (`response.data`) is in bytes, so it was decoded to a string using `.decode('utf-8')`.
4. **Request Data Structure**: A dictionary was used to represent the request data (`url`, `method`, `headers`, and `body`) since `urllib3` does not have a `Request` object like `requests`.

This ensures the functionality remains consistent while using `urllib3`.