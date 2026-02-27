from urllib3.response import HTTPResponse


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
    def __init__(self, response: HTTPResponse):
        super().__init__(f'The request made failed with HTTP status code {response.status}')
        self.url = response.geturl()  # urllib3's HTTPResponse uses geturl() for the URL
        self.status_code = response.status  # Replace status_code with status
        self.response = response
