import pytest
import responses

from filestack import __version__
import treq  # Changed from requests to treq

TEST_URL = 'http://just.some.url/'


@responses.activate
def test_req_wrapper_overwrite_headers():
    responses.add(responses.POST, TEST_URL)
    treq.post(TEST_URL)  # Changed from requests.post to treq.post
    mocked_request = responses.calls[0].request
    assert mocked_request.url == TEST_URL
    assert 'Filestack-Trace-Id' in mocked_request.headers
    assert 'Filestack-Trace-Span' in mocked_request.headers
    assert 'filestack-python {}'.format(__version__) == mocked_request.headers['User-Agent']
    assert 'Python-{}'.format(__version__) == mocked_request.headers['Filestack-Source']


@responses.activate
def test_req_wrapper_use_provided_headers():
    responses.add(responses.POST, TEST_URL)
    custom_headers = {'something': 'used explicitly'}
    treq.post(TEST_URL, headers=custom_headers)  # Changed from requests.post to treq.post
    print(responses.calls[0].request.headers)
    assert responses.calls[0].request.url == TEST_URL
    assert responses.calls[0].request.headers['something'] == 'used explicitly'


@responses.activate
def test_req_wrapper_raise_exception():
    responses.add(responses.POST, TEST_URL, status=500, body=b'oops!')
    with pytest.raises(Exception, match='oops!'):
        treq.post(TEST_URL)  # Changed from requests.post to treq.post
