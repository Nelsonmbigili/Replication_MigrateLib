import aiohttp
from .response import Response
import smartystreets_python_sdk as smarty
import smartystreets_python_sdk_version as version


class RequestsSender:
    def __init__(self, max_timeout=None, proxy=None, ip=None):
        self.session = aiohttp.ClientSession()
        self.max_timeout = max_timeout or 10
        self.proxy = proxy
        self.debug = None
        self.ip = ip

    async def send(self, smarty_request):
        ip = self.ip
        request_data = build_request(smarty_request, ip)
        proxy = self.build_proxies()

        if self.debug:
            print_request_data(request_data)

        try:
            async with self.session.request(
                method=request_data['method'],
                url=request_data['url'],
                headers=request_data['headers'],
                params=request_data['params'],
                data=request_data['data'],
                proxy=proxy,
                timeout=aiohttp.ClientTimeout(total=self.max_timeout)
            ) as response:
                if self.debug:
                    await print_response_data(response)
                return await build_smarty_response(response)
        except aiohttp.ClientError as e:
            return build_smarty_response(None, error=str(e))

    def build_proxies(self):
        if not self.proxy:
            return None
        if self.proxy.host in ['http://', 'https://']:
            raise smarty.exceptions.SmartyException('Proxy must have a valid host (including port)')

        proxy_string = self.proxy.host

        if self.proxy.username:
            proxy_string = '{}:{}@{}'.format(self.proxy.username, self.proxy.password, proxy_string)

        return proxy_string


def build_request(smarty_request, ip=None):
    try:
        headers = {
            'User-Agent': "smartystreets (sdk:python@{})".format(version.__version__),
            'Content-Type': smarty_request.content_type
        }
        if smarty_request.referer:
            headers['Referer'] = smarty_request.referer
        if ip is not None:
            headers['X-Forwarded-For'] = ip

        method = 'POST' if smarty_request.payload else 'GET'
        data = smarty_request.payload if smarty_request.payload else None

        return {
            'url': smarty_request.url_prefix,
            'params': smarty_request.parameters,
            'headers': headers,
            'data': data,
            'method': method
        }
    except AttributeError:
        return smarty_request


async def build_smarty_response(inner_response, error=None):
    if inner_response is None:
        return Response(None, 0, {}, error)

    text = await inner_response.text()
    return Response(text, inner_response.status, inner_response.headers, error)


def print_request_data(request):
    print(request['method'])
    print()
    print('URL: {}\r\n'.format(request['url']))
    print('Headers:')
    for header, value in request['headers'].items():
        print('  {}: {}'.format(header, value))
    print()
    print('Body: ')
    print('  {}\r\n'.format(request['data']))


async def print_response_data(response):
    print('****** Response ******\r\n')
    print(response.status)
    print()
    print(await response.text())
    print('**********************\r\n')
