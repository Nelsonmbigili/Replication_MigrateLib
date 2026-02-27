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
@pytest.mark.asyncio
async def test_req_wrapper_raise_exception(stub_treq):
    resource = MockResource(response_code=500, response_body=b'oops!')
    stub_treq = StubTreq(Site(resource))

    with pytest.raises(Exception, match='oops!'):
        await stub_treq.post(TEST_URL)
