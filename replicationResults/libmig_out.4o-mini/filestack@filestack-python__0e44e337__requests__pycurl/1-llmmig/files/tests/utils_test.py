import pytest
import responses
import pycurl
from io import BytesIO

from filestack import __version__
from filestack.utils import requests

TEST_URL = 'http://just.some.url/'

def pycurl_post(url, headers=None):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.POST, 1)
    
    if headers:
        c.setopt(c.HTTPHEADER, headers)
    
    try:
        c.perform()
    except pycurl.error as e:
        raise Exception(e.args[1])  # Raise the error message from pycurl
    finally:
        c.close()
    
    return buffer.getvalue()

@responses.activate
def test_req_wrapper_overwrite_headers():
    responses.add(responses.POST, TEST_URL)
    pycurl_post(TEST_URL)
    mocked_request = responses.calls[0].request
    assert mocked_request.url == TEST_URL
    assert 'Filestack-Trace-Id' in mocked_request.headers
    assert 'Filestack-Trace-Span' in mocked_request.headers
    assert 'filestack-python {}'.format(__version__) == mocked_request.headers['User-Agent']
    assert 'Python-{}'.format(__version__) == mocked_request.headers['Filestack-Source']


@responses.activate
def test_req_wrapper_use_provided_headers():
    responses.add(responses.POST, TEST_URL)
    custom_headers = ['something: used explicitly']
    pycurl_post(TEST_URL, headers=custom_headers)
    print(responses.calls[0].request.headers)
    assert responses.calls[0].request.url == TEST_URL
    assert responses.calls[0].request.headers['something'] == 'used explicitly'


@responses.activate
def test_req_wrapper_raise_exception():
    responses.add(responses.POST, TEST_URL, status=500, body=b'oops!')
    with pytest.raises(Exception, match='oops!'):
        pycurl_post(TEST_URL)
