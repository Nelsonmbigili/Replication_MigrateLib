import pytest
from aioresponses import aioresponses
from filestack import __version__
from filestack.utils import requests

TEST_URL = 'http://just.some.url/'


@pytest.mark.asyncio
@aioresponses()
async def test_req_wrapper_overwrite_headers(mocked):
    mocked.post(TEST_URL)
    async with requests.ClientSession() as session:
        async with session.post(TEST_URL) as response:
            mocked_request = mocked.requests[('POST', TEST_URL)][0]
            assert mocked_request.url == TEST_URL
            assert 'Filestack-Trace-Id' in mocked_request.headers
            assert 'Filestack-Trace-Span' in mocked_request.headers
            assert 'filestack-python {}'.format(__version__) == mocked_request.headers['User-Agent']
            assert 'Python-{}'.format(__version__) == mocked_request.headers['Filestack-Source']


@pytest.mark.asyncio
@aioresponses()
async def test_req_wrapper_use_provided_headers(mocked):
    mocked.post(TEST_URL)
    custom_headers = {'something': 'used explicitly'}
    async with requests.ClientSession() as session:
        async with session.post(TEST_URL, headers=custom_headers) as response:
            mocked_request = mocked.requests[('POST', TEST_URL)][0]
            print(mocked_request.headers)
            assert mocked_request.url == TEST_URL
            assert mocked_request.headers['something'] == 'used explicitly'


@pytest.mark.asyncio
@aioresponses()
async def test_req_wrapper_raise_exception(mocked):
    mocked.post(TEST_URL, status=500, body=b'oops!')
    with pytest.raises(Exception, match='oops!'):
        async with requests.ClientSession() as session:
            async with session.post(TEST_URL) as response:
                response.raise_for_status()
