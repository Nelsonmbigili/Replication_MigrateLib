import pycurl
from io import BytesIO


class NuException(Exception):

    def __init__(self, message):
        super().__init__(message)


class NuInvalidAuthenticationMethod(NuException):
    def __init__(self, message):
        super().__init__(message)


class NuMissingCreditCard(NuException):
    def __init__(self):
        super().__init__(f'Couldn\'t fetch bills due to missing credit card.')


class NuRequestException(NuException):
    def __init__(self, curl: pycurl.Curl):
        buffer = BytesIO()
        curl.setopt(curl.WRITEFUNCTION, buffer.write)
        curl.perform()
        http_code = curl.getinfo(curl.RESPONSE_CODE)
        url = curl.getinfo(curl.EFFECTIVE_URL)
        super().__init__(f'The request made failed with HTTP status code {http_code}')
        self.url = url
        self.status_code = http_code
        self.response = buffer.getvalue()
