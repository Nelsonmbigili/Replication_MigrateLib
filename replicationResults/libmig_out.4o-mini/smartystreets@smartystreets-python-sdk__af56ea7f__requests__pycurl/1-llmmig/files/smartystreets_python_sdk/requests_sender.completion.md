### Explanation of Changes

To migrate the code from using the `requests` library to the `pycurl` library, several key changes were made:

1. **Session Management**: The `requests.Session` object was replaced with `pycurl.Curl()`, as `pycurl` does not have a session concept like `requests`.
2. **Request Preparation**: The `requests` method of preparing a request was replaced with direct `pycurl` method calls to set options for the request.
3. **Sending Requests**: Instead of using `session.send()`, the `pycurl` library requires the use of `perform()` to execute the request.
4. **Response Handling**: The response handling was adjusted to read from a `BytesIO` object since `pycurl` does not return a response object directly like `requests`.
5. **Proxy Configuration**: The proxy settings were adapted to fit the `pycurl` format.
6. **Error Handling**: The error handling was simplified to fit the `pycurl` response model.

Here is the modified code:

```python
from io import BytesIO
import pycurl
from .response import Response
import smartystreets_python_sdk as smarty
import smartystreets_python_sdk_version as version


class RequestsSender:
    def __init__(self, max_timeout=None, proxy=None, ip=None):
        self.max_timeout = max_timeout or 10
        self.proxy = proxy
        self.debug = None
        self.ip = ip

    def send(self, smarty_request):
        ip = self.ip
        request = build_request(smarty_request, ip)
        response_buffer = BytesIO()
        curl = pycurl.Curl()
        
        curl.setopt(curl.URL, request.url)
        curl.setopt(curl.WRITEFUNCTION, response_buffer.write)
        curl.setopt(curl.TIMEOUT, self.max_timeout)

        if request.method == 'POST':
            curl.setopt(curl.POST, 1)
            curl.setopt(curl.POSTFIELDS, request.data)
        
        headers = [f"{key}: {value}" for key, value in request.headers.items()]
        curl.setopt(curl.HTTPHEADER, headers)

        prepped_proxies = self.build_proxies()
        if prepped_proxies:
            curl.setopt(curl.PROXY, prepped_proxies.get('http', prepped_proxies.get('https', None)))

        if self.debug:
            print_request_data(request)

        try:
            curl.perform()
            response_code = curl.getinfo(curl.RESPONSE_CODE)
            response_body = response_buffer.getvalue().decode('utf-8')
            if self.debug:
                print_response_data(response_code, response_body)
            return build_smarty_response(response_body, response_code)
        finally:
            curl.close()

    def build_proxies(self):
        if not self.proxy:
            return {}
        if (self.proxy.host == 'http://' or self.proxy.host =='https://'):
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


def build_smarty_response(inner_response, status_code, error=None):
    return Response(inner_response, status_code, {}, error)


def print_request_data(request):
    print(request.method)
    print()
    print('URL: {}\r\n'.format(request.url))
    print('Headers:')
    for header in request.headers:
        print('  {}: {}'.format(header, request.headers[header]))
    print()
    print('Body: ')
    print('  {}\r\n'.format(request.data))


def print_response_data(response_code, response_body):
    print('****** Response ******\r\n')
    print(response_code)
    print()
    print(response_body)
    print('**********************\r\n')
```

This code now uses `pycurl` for making HTTP requests while maintaining the original structure and functionality of the application.