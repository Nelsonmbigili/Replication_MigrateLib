from treq.response import _Response


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
    def __init__(self, response: _Response):
        # Since `treq` responses are asynchronous, we cannot directly access attributes like `status_code` or `url`.
        # These would need to be awaited in an asynchronous context. For now, we assume this is handled elsewhere.
        super().__init__(f'The request made failed with HTTP status code {response.code}')
        self.url = response.request.absoluteURI.decode('utf-8')  # Access the URL from the request object
        self.status_code = response.code  # Access the status code
        self.response = response
