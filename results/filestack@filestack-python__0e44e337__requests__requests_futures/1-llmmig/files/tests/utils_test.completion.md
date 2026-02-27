### Explanation of Changes
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: The `requests` module from `filestack.utils` was replaced with `requests_futures.sessions.FuturesSession`. This is because `requests_futures` provides asynchronous functionality via the `FuturesSession` class.
2. **Session Initialization**: A `FuturesSession` object was created to replace the direct use of `requests.post`. This is necessary because `requests_futures` requires a session object to make asynchronous requests.
3. **Method Calls**: The `post` method of the `FuturesSession` object was used instead of `requests.post`.
4. **Responses Library Compatibility**: Since `responses` is used to mock HTTP requests, it works with synchronous requests. To maintain compatibility, the `.result()` method was called on the future object returned by `FuturesSession.post()` to block and wait for the response, ensuring synchronous behavior.

### Modified Code
```python
import pytest
import responses

from filestack import __version__
from requests_futures.sessions import FuturesSession

TEST_URL = 'http://just.some.url/'

# Create a FuturesSession instance
session = FuturesSession()


@responses.activate
def test_req_wrapper_overwrite_headers():
    responses.add(responses.POST, TEST_URL)
    # Use session.post and call .result() to block and get the response
    session.post(TEST_URL).result()
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
    # Use session.post and call .result() to block and get the response
    session.post(TEST_URL, headers=custom_headers).result()
    print(responses.calls[0].request.headers)
    assert responses.calls[0].request.url == TEST_URL
    assert responses.calls[0].request.headers['something'] == 'used explicitly'


@responses.activate
def test_req_wrapper_raise_exception():
    responses.add(responses.POST, TEST_URL, status=500, body=b'oops!')
    with pytest.raises(Exception, match='oops!'):
        # Use session.post and call .result() to block and get the response
        session.post(TEST_URL).result()
```

### Key Notes
- The `FuturesSession.post()` method returns a future object. To maintain synchronous behavior (as required by the `responses` library), the `.result()` method was called to block until the request completes.
- No other parts of the code were modified, ensuring compatibility with the rest of the application.