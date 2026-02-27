import io
import json
from collections import defaultdict

import pytest
from aioresponses import aioresponses

from filestack import Client
from filestack import config
from filestack.uploads.multipart import upload_chunk, Chunk

APIKEY = 'APIKEY'
HANDLE = 'SOMEHANDLE'


@pytest.fixture
async def multipart_mock():
    async with aioresponses() as rsps:
        rsps.post(
            config.MULTIPART_START_URL,
            status=200,
            payload={
                'region': 'us-east-1', 'upload_id': 'someuuid', 'uri': 'someuri',
                'location_url': 'fs-uploads.com'
            }
        )
        rsps.post(
            'https://fs-uploads.com/multipart/upload',
            status=200,
            payload={'url': 'http://somewhere.on.s3', 'headers': {'filestack': 'header'}}
        )
        rsps.put('http://somewhere.on.s3', status=200, headers={'ETag': 'abc'})
        rsps.post(
            'https://fs-uploads.com/multipart/complete',
            status=200,
            payload={'url': 'https://cdn.filestackcontent.com/{}'.format(HANDLE), 'handle': HANDLE}
        )
        yield rsps


@pytest.mark.asyncio
async def test_upload_filepath(multipart_mock):
    client = Client(APIKEY)
    filelink = await client.upload(filepath='tests/data/doom.mp4')
    assert filelink.handle == HANDLE
    assert filelink.upload_response == {'url': 'https://cdn.filestackcontent.com/{}'.format(HANDLE), 'handle': HANDLE}


@pytest.mark.asyncio
async def test_upload_file_obj(multipart_mock):
    file_content = b'file bytes'
    filelink = await Client(APIKEY).upload(file_obj=io.BytesIO(file_content))
    assert filelink.handle == HANDLE
    assert multipart_mock.requests[2].kwargs['headers']['filestack'] == 'header'
    assert multipart_mock.requests[2].kwargs['data'] == file_content


@pytest.mark.asyncio
async def test_upload_with_workflows(multipart_mock):
    workflow_ids = ['workflow-id-1', 'workflow-id-2']
    store_params = {'workflows': workflow_ids}
    client = Client(APIKEY)
    filelink = await client.upload(filepath='tests/data/bird.jpg', store_params=store_params)
    assert filelink.handle == HANDLE
    multipart_complete_payload = json.loads(multipart_mock.requests[3].kwargs['data'].decode())
    assert multipart_complete_payload['store']['workflows'] == workflow_ids


@pytest.mark.asyncio
async def test_upload_chunk():
    async with aioresponses() as rsps:
        rsps.post(
            'https://fsuploads.com/multipart/upload',
            status=200,
            payload={'url': 'http://s3-upload.url', 'headers': {}}
        )
        rsps.put('http://s3-upload.url', status=200, headers={'ETag': 'etagX'})

        chunk = Chunk(num=123, seek_point=0, filepath='tests/data/doom.mp4')
        start_response = defaultdict(str)
        start_response['location_url'] = 'fsuploads.com'
        upload_result = await upload_chunk('apikey', 'filename', 's3', start_response, chunk)
        assert upload_result == {'part_number': 123, 'etag': 'etagX'}
