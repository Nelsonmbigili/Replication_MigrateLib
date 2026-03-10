### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the primary change involves replacing the synchronous `requests.post` calls with the asynchronous equivalent provided by `requests_futures`. This is done by using `FuturesSession` from the `requests_futures.sessions` module. The `FuturesSession` allows for non-blocking requests, which means that the code can continue executing while waiting for the response. Additionally, we need to handle the response differently since it is now a future object.

### Modified Code
Here is the modified code after migrating to `requests_futures`:

```python
import pytest
import responses
from requests_futures.sessions import FuturesSession

from filestack import __version__
from filestack.utils import requests

TEST_URL = 'http://just.some.url/'

# Create a FuturesSession instance
session = FuturesSession()

@responses.activate
def test_req_wrapper_overwrite_headers():
    responses.add(responses.POST, TEST_URL)
    future = session.post(TEST_URL)
    response = future.result()  # Wait for the response
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
    future = session.post(TEST_URL, headers=custom_headers)
    response = future.result()  # Wait for the response
    print(responses.calls[0].request.headers)
    assert responses.calls[0].request.url == TEST_URL
    assert responses.calls[0].request.headers['something'] == 'used explicitly'


@responses.activate
def test_req_wrapper_raise_exception():
    responses.add(responses.POST, TEST_URL, status=500, body=b'oops!')
    future = session.post(TEST_URL)
    with pytest.raises(Exception, match='oops!'):
        future.result()  # Wait for the response to raise the exception
```

In this modified code, we replaced the direct calls to `requests.post` with `session.post`, and we added `future.result()` to wait for the response before proceeding with assertions or exception handling. This ensures that the code behaves correctly in an asynchronous context.