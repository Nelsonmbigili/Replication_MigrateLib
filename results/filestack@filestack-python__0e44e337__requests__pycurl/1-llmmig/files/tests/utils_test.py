import pytest
import io
import pycurl

from filestack import __version__

TEST_URL = 'http://just.some.url/'


def mock_pycurl_post(url, headers=None, body=None, status=200):
    """
    Mock function to simulate pycurl POST requests.
    """
    class MockResponse:
        def __init__(self, url, headers, body, status):
            self.url = url
            self.headers = headers
            self.body = body
            self.status = status

    return MockResponse(url, headers, body, status)


def pycurl_post(url, headers=None):
    """
    Perform a POST request using pycurl.
    """
    buffer = io.BytesIO()
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.POST, 1)
    if headers:
        curl.setopt(pycurl.HTTPHEADER, [f"{key}: {value}" for key, value in headers.items()])
    curl.setopt(pycurl.WRITEDATA, buffer)
    try:
        curl.perform()
        status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        if status_code >= 400:
            raise Exception(buffer.getvalue().decode('utf-8'))
    finally:
        curl.close()
    return buffer.getvalue().decode('utf-8')


def test_req_wrapper_overwrite_headers():
    mock_response = mock_pycurl_post(TEST_URL)
    headers = {
        'Filestack-Trace-Id': 'some-trace-id',
        'Filestack-Trace-Span': 'some-trace-span',
        'User-Agent': f'filestack-python {__version__}',
        'Filestack-Source': f'Python-{__version__}',
    }
    response = pycurl_post(TEST_URL, headers=headers)
    assert mock_response.url == TEST_URL
    assert 'Filestack-Trace-Id' in headers
    assert 'Filestack-Trace-Span' in headers
    assert f'filestack-python {__version__}' == headers['User-Agent']
    assert f'Python-{__version__}' == headers['Filestack-Source']


def test_req_wrapper_use_provided_headers():
    mock_response = mock_pycurl_post(TEST_URL)
    custom_headers = {'something': 'used explicitly'}
    response = pycurl_post(TEST_URL, headers=custom_headers)
    print(custom_headers)
    assert mock_response.url == TEST_URL
    assert custom_headers['something'] == 'used explicitly'


def test_req_wrapper_raise_exception():
    mock_response = mock_pycurl_post(TEST_URL, status=500, body=b'oops!')
    with pytest.raises(Exception, match='oops!'):
        pycurl_post(TEST_URL)
