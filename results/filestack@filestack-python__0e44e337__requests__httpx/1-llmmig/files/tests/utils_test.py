import pytest
import respx
from httpx import Response

from filestack import __version__
from filestack.utils import httpx

TEST_URL = 'http://just.some.url/'


@respx.mock
def test_req_wrapper_overwrite_headers():
    respx.post(TEST_URL).mock(return_value=Response(200))
    httpx.post(TEST_URL)
    mocked_request = respx.calls[0].request
    assert mocked_request.url == TEST_URL
    assert 'Filestack-Trace-Id' in mocked_request.headers
    assert 'Filestack-Trace-Span' in mocked_request.headers
    assert 'filestack-python {}'.format(__version__) == mocked_request.headers['User-Agent']
    assert 'Python-{}'.format(__version__) == mocked_request.headers['Filestack-Source']


@respx.mock
def test_req_wrapper_use_provided_headers():
    respx.post(TEST_URL).mock(return_value=Response(200))
    custom_headers = {'something': 'used explicitly'}
    httpx.post(TEST_URL, headers=custom_headers)
    print(respx.calls[0].request.headers)
    assert respx.calls[0].request.url == TEST_URL
    assert respx.calls[0].request.headers['something'] == 'used explicitly'


@respx.mock
def test_req_wrapper_raise_exception():
    respx.post(TEST_URL).mock(return_value=Response(500, content=b'oops!'))
    with pytest.raises(Exception, match='oops!'):
        httpx.post(TEST_URL)
