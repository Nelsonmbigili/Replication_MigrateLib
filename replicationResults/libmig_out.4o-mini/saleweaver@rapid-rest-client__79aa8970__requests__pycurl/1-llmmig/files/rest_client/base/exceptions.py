from typing import Any
import pycurl
from io import BytesIO

from requests.structures import CaseInsensitiveDict


class ApiException(Exception):
    def __init__(self, data: Any = None, headers: CaseInsensitiveDict = None, status_code: int = None, *args, **kwargs):
        self.data = data or kwargs
        self.headers = headers
        self.status_code = status_code


class ConfigurationException(Exception):
    pass

# Example function to demonstrate how to use pycurl for a GET request
def make_request(url: str):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])
    
    try:
        c.perform()
        status_code = c.getinfo(c.RESPONSE_CODE)
        response_data = buffer.getvalue().decode('utf-8')
        return status_code, response_data
    except pycurl.error as e:
        raise ApiException(data=str(e), status_code=e.args[0])
    finally:
        c.close()
