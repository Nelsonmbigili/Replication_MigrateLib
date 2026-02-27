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
