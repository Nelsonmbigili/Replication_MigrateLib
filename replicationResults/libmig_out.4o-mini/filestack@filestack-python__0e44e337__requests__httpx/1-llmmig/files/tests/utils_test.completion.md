### Explanation of Changes
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:

1. **Import Statement**: The import for `requests` was changed to import `httpx`.
2. **Function Calls**: The `requests.post` function calls were replaced with `httpx.post`. The `httpx` library uses a similar API, so the function calls remain largely the same.
3. **Response Handling**: The `responses` library is still used for mocking, but since `httpx` does not have a built-in way to handle responses like `requests`, the mocking remains unchanged.

The overall structure and logic of the tests remain intact, ensuring that the migration does not affect the functionality of the tests.

### Modified Code
```python
import pytest
import responses

from filestack import __version__
from filestack.utils import httpx  # Changed from requests to httpx

TEST_URL = 'http://just.some.url/'


@responses.activate
def test_req_wrapper_overwrite_headers():
    responses.add(responses.POST, TEST_URL)
    httpx.post(TEST_URL)  # Changed from requests.post to httpx.post
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
    httpx.post(TEST_URL, headers=custom_headers)  # Changed from requests.post to httpx.post
    print(responses.calls[0].request.headers)
    assert responses.calls[0].request.url == TEST_URL
    assert responses.calls[0].request.headers['something'] == 'used explicitly'


@responses.activate
def test_req_wrapper_raise_exception():
    responses.add(responses.POST, TEST_URL, status=500, body=b'oops!')
    with pytest.raises(Exception, match='oops!'):
        httpx.post(TEST_URL)  # Changed from requests.post to httpx.post
```