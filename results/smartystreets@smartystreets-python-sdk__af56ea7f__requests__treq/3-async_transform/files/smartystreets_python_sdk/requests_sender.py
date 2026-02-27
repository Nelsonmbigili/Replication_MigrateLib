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
