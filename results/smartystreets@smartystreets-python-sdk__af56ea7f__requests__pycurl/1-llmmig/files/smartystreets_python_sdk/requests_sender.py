import pycurl
from io import BytesIO
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
        curl = pycurl.Curl()
        response_buffer = BytesIO()
        header_buffer = BytesIO()

        try:
            build_request(curl, smarty_request, ip)
            prepped_proxies = self.build_proxies(curl)

            curl.setopt(pycurl.WRITEFUNCTION, response_buffer.write)
            curl.setopt(pycurl.HEADERFUNCTION, header_buffer.write)
            curl.setopt(pycurl.TIMEOUT, self.max_timeout)

            if self.debug:
                curl.setopt(pycurl.VERBOSE, True)

            curl.perform()

            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
            response_body = response_buffer.getvalue().decode('utf-8')
            response_headers = header_buffer.getvalue().decode('utf-8')

            if self.debug:
                print_response_data(status_code, response_headers, response_body)

            return build_smarty_response(response_body, status_code, response_headers)
        except pycurl.error as e:
            return build_smarty_response(None, error=str(e))
        finally:
            curl.close()

    def build_proxies(self, curl):
        if not self.proxy:
            return
        if self.proxy.host == 'http://' or self.proxy.host == 'https://':
            raise smarty.exceptions.SmartyException('Proxy must have a valid host (including port)')

        proxy_string = self.proxy.host
        if self.proxy.username:
            proxy_auth = '{}:{}'.format(self.proxy.username, self.proxy.password)
            curl.setopt(pycurl.PROXYUSERPWD, proxy_auth)

        curl.setopt(pycurl.PROXY, proxy_string)


def build_request(curl, smarty_request, ip=None):
    try:
        curl.setopt(pycurl.URL, smarty_request.url_prefix)
        headers = [
            "User-Agent: smartystreets (sdk:python@{})".format(version.__version__),
            "Content-Type: {}".format(smarty_request.content_type),
        ]
        if smarty_request.referer:
            headers.append("Referer: {}".format(smarty_request.referer))
        if ip is not None:
            headers.append("X-Forwarded-For: {}".format(ip))

        if smarty_request.payload:
            curl.setopt(pycurl.POST, 1)
            curl.setopt(pycurl.POSTFIELDS, smarty_request.payload)
        else:
            curl.setopt(pycurl.HTTPGET, 1)

        curl.setopt(pycurl.HTTPHEADER, headers)
    except AttributeError:
        pass


def build_smarty_response(body, status_code=None, headers=None, error=None):
    return Response(body, status_code, headers, error)


def print_request_data(curl):
    print('****** Request ******\r\n')
    print('URL: {}\r\n'.format(curl.getinfo(pycurl.EFFECTIVE_URL)))
    print('**********************\r\n')


def print_response_data(status_code, headers, body):
    print('****** Response ******\r\n')
    print('Status Code: {}\r\n'.format(status_code))
    print('Headers:\r\n{}'.format(headers))
    print('Body:\r\n{}'.format(body))
    print('**********************\r\n')
