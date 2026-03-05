import pytest
import responses
import urllib3

from filestack import __version__

TEST_URL = 'http://just.some.url/'
http = urllib3.PoolManager()

@responses.activate
def test_req_wrapper_overwrite_headers():
    responses.add(responses.POST, TEST_URL)
    response = http.request('POST', TEST_URL)
    assert response.url == TEST_URL
    assert 'Filestack-Trace-Id' in response.headers
    assert 'Filestack-Trace-Span' in response.headers
    assert 'filestack-python {}'.format(__version__) == response.headers['User-Agent']
    assert 'Python-{}'.format(__version__) == response.headers['Filestack-Source']


@responses.activate
def test_req_wrapper_use_provided_headers():
    responses.add(responses.POST, TEST_URL)
    custom_headers = {'something': 'used explicitly'}
    response = http.request('POST', TEST_URL, headers=custom_headers)
    print(response.headers)
    assert response.url == TEST_URL
    assert response.headers['something'] == 'used explicitly'


@responses.activate
def test_req_wrapper_raise_exception():
    responses.add(responses.POST, TEST_URL, status=500, body=b'oops!')
    with pytest.raises(Exception, match='oops!'):
        http.request('POST', TEST_URL)
