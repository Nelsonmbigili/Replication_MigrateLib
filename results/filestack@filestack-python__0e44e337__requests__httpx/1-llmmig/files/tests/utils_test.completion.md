### Explanation of Changes:
To migrate the code from using the `requests` library to `httpx`, the following changes were made:
1. **Library Import**: The `requests` module from `filestack.utils` was replaced with `httpx`.
2. **Mocking HTTP Requests**: The `responses` library is designed to work with `requests`. Since `httpx` is being used, the `respx` library (a mocking library for `httpx`) was used instead.
3. **Mocking Setup**: The `responses.activate` decorator was replaced with `respx.mock`. The `responses.add` calls were replaced with `respx` route definitions.
4. **Request Calls**: The `requests.post` calls were replaced with `httpx.post`.
5. **Accessing Mocked Requests**: The `responses.calls` attribute was replaced with `respx.calls` to access the mocked requests and their details.

### Modified Code:
```python
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
```

### Key Notes:
- The `respx` library is used to mock HTTP requests for `httpx`, as `responses` is specific to `requests`.
- The `respx.calls` attribute provides access to the mocked requests, similar to `responses.calls`.
- The `httpx.post` method is used in place of `requests.post`.
- The rest of the code structure, including function names and assertions, remains unchanged to ensure compatibility with the larger application.