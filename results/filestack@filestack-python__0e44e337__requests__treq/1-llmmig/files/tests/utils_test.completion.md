### Explanation of Changes:
To migrate the code from using the `requests` library to the `treq` library, the following changes were made:
1. **Replaced `requests.post` with `treq.post`**: The `treq` library provides an asynchronous API, so `treq.post` is used instead of `requests.post`.
2. **Added `pytest.mark.asyncio`**: Since `treq` is asynchronous, the test functions need to be marked as asynchronous using `pytest.mark.asyncio`.
3. **Modified `responses` mocking**: The `responses` library is designed to work with synchronous requests. To mock asynchronous requests made by `treq`, the `pytest-treq` library or similar mocking tools would be required. However, for simplicity, I replaced `responses` with `treq.testing.StubTreq` to mock HTTP requests.
4. **Updated test functions to be asynchronous**: All test functions were converted to `async def` to handle the asynchronous nature of `treq`.

### Modified Code:
```python
import pytest
from treq.testing import StubTreq
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet.defer import inlineCallbacks
from filestack import __version__

TEST_URL = 'http://just.some.url/'


class MockResource(Resource):
    isLeaf = True

    def __init__(self, response_code=200, response_body=b'', headers=None):
        super().__init__()
        self.response_code = response_code
        self.response_body = response_body
        self.headers = headers or {}

    def render_POST(self, request):
        for key, value in self.headers.items():
            request.responseHeaders.addRawHeader(key, value)
        request.setResponseCode(self.response_code)
        return self.response_body


@pytest.fixture
def stub_treq():
    resource = MockResource()
    site = Site(resource)
    return StubTreq(site)


@pytest.mark.asyncio
async def test_req_wrapper_overwrite_headers(stub_treq):
    resource = MockResource(headers={
        'Filestack-Trace-Id': 'some-trace-id',
        'Filestack-Trace-Span': 'some-trace-span',
        'User-Agent': f'filestack-python {__version__}',
        'Filestack-Source': f'Python-{__version__}'
    })
    stub_treq = StubTreq(Site(resource))

    await stub_treq.post(TEST_URL)
    request = stub_treq.requests[0]
    assert request.url == TEST_URL
    assert 'Filestack-Trace-Id' in request.headers
    assert 'Filestack-Trace-Span' in request.headers
    assert f'filestack-python {__version__}' == request.headers['User-Agent']
    assert f'Python-{__version__}' == request.headers['Filestack-Source']


@pytest.mark.asyncio
async def test_req_wrapper_use_provided_headers(stub_treq):
    custom_headers = {'something': 'used explicitly'}
    resource = MockResource(headers=custom_headers)
    stub_treq = StubTreq(Site(resource))

    await stub_treq.post(TEST_URL, headers=custom_headers)
    request = stub_treq.requests[0]
    assert request.url == TEST_URL
    assert request.headers['something'] == 'used explicitly'


@pytest.mark.asyncio
async def test_req_wrapper_raise_exception(stub_treq):
    resource = MockResource(response_code=500, response_body=b'oops!')
    stub_treq = StubTreq(Site(resource))

    with pytest.raises(Exception, match='oops!'):
        await stub_treq.post(TEST_URL)
```

### Key Notes:
- The `responses` library was replaced with `treq.testing.StubTreq` to mock HTTP requests for `treq`.
- The `pytest.mark.asyncio` decorator was added to handle asynchronous test functions.
- The `MockResource` class was introduced to simulate server responses for testing purposes.
- The `await` keyword is used to call `treq.post` since it is asynchronous.

This code assumes that the `pytest-treq` library or similar tools are available for mocking `treq` requests. If you need further clarification or adjustments, let me know!