import pytest
import responses
import urllib3

from filestack import __version__

TEST_URL = 'http://just.some.url/'

# Create a PoolManager instance for making HTTP requests
http = urllib3.PoolManager()


def post(url, headers=None):
    """
    A wrapper function to replace `requests.post` with `urllib3` functionality.
    """
    try:
        response = http.request(
            'POST',
            url,
            headers=headers
        )
        if response.status >= 400:
            raise Exception(response.data.decode('utf-8'))
        return response
    except urllib3.exceptions.HTTPError as e:
        raise Exception(str(e))


@responses.activate
def test_req_wrapper_overwrite_headers():
    responses.add(responses.POST, TEST_URL)
    post(TEST_URL)
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
    post(TEST_URL, headers=custom_headers)
    print(responses.calls[0].request.headers)
    assert responses.calls[0].request.url == TEST_URL
    assert responses.calls[0].request.headers['something'] == 'used explicitly'


@responses.activate
def test_req_wrapper_raise_exception():
    responses.add(responses.POST, TEST_URL, status=500, body=b'oops!')
    with pytest.raises(Exception, match='oops!'):
        post(TEST_URL)
