import pytest
import aiohttp
import asyncio
from filestack import __version__

TEST_URL = 'http://just.some.url/'

async def post_request(url, headers=None):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers) as response:
            return response

@pytest.mark.asyncio
async def test_req_wrapper_overwrite_headers():
    async with aiohttp.ClientSession() as session:
        async with session.post(TEST_URL) as response:
            assert response.status == 200
            mocked_request = response.request_info
            assert mocked_request.url == TEST_URL
            assert 'Filestack-Trace-Id' in mocked_request.headers
            assert 'Filestack-Trace-Span' in mocked_request.headers
            assert 'filestack-python {}'.format(__version__) == mocked_request.headers['User-Agent']
            assert 'Python-{}'.format(__version__) == mocked_request.headers['Filestack-Source']

@pytest.mark.asyncio
async def test_req_wrapper_use_provided_headers():
    custom_headers = {'something': 'used explicitly'}
    async with aiohttp.ClientSession() as session:
        async with session.post(TEST_URL, headers=custom_headers) as response:
            assert response.status == 200
            mocked_request = response.request_info
            assert mocked_request.url == TEST_URL
            assert mocked_request.headers['something'] == 'used explicitly'

@pytest.mark.asyncio
async def test_req_wrapper_raise_exception():
    async with aiohttp.ClientSession() as session:
        async with session.post(TEST_URL) as response:
            if response.status == 500:
                raise Exception('oops!')
