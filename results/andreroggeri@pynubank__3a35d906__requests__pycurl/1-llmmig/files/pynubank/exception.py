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


class CustomResponse:
    """
    A custom response class to mimic the behavior of requests.Response
    for use with pycurl.
    """
    def __init__(self, url, status_code, content):
        self.url = url
        self.status_code = status_code
        self.content = content


class NuRequestException(NuException):
    def __init__(self, response: CustomResponse):
        super().__init__(f'The request made failed with HTTP status code {response.status_code}')
        self.url = response.url
        self.status_code = response.status_code
        self.response = response


# Example function to demonstrate how to use pycurl to make a request
def make_request(url):
    buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.WRITEDATA, buffer)
    
    try:
        curl.perform()
        status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        response_url = curl.getinfo(pycurl.EFFECTIVE_URL)
    except pycurl.error as e:
        raise NuException(f'An error occurred while making the request: {e}')
    finally:
        curl.close()

    # Create a CustomResponse object to mimic the behavior of requests.Response
    response_content = buffer.getvalue().decode('utf-8')
    return CustomResponse(url=response_url, status_code=status_code, content=response_content)
