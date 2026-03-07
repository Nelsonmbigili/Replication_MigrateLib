import io
import json
from collections import defaultdict

import httpx
import pytest

from filestack import Client
from filestack import config
from filestack.uploads.multipart import upload_chunk, Chunk

APIKEY = 'APIKEY'
HANDLE = 'SOMEHANDLE'


@pytest.fixture
def multipart_mock(httpx_mock):
    httpx_mock.add_response(
        method='POST', url=config.MULTIPART_START_URL, status_code=200,
        json={
            'region': 'us-east-1', 'upload_id': 'someuuid', 'uri': 'someuri',
            'location_url': 'fs-uploads.com'
        }
    )
    httpx_mock.add_response(
        method='POST', url='https://fs-uploads.com/multipart/upload',
        status_code=200, json={'url': 'http://somewhere.on.s3', 'headers': {'filestack': 'header'}}
    )
    httpx_mock.add_response(method='PUT', url='http://somewhere.on.s3', json={}, headers={'ETag': 'abc'})
    httpx_mock.add_response(
        method='POST', url='https://fs-uploads.com/multipart/complete', status_code=200,
        json={'url': 'https://cdn.filestackcontent.com/{}'.format(HANDLE), 'handle': HANDLE}
    )


def test_upload_filepath(multipart_mock):
    client = Client(APIKEY)
    filelink = client.upload(filepath='tests/data/doom.mp4')
    assert filelink.handle == HANDLE
    assert filelink.upload_response == {'url': 'https://cdn.filestackcontent.com/{}'.format(HANDLE), 'handle': HANDLE}


def test_upload_file_obj(multipart_mock):
    file_content = b'file bytes'
    filelink = Client(APIKEY).upload(file_obj=io.BytesIO(file_content))
    assert filelink.handle == HANDLE
    assert multipart_mock.calls[2].request.headers['filestack'] == 'header'
    assert multipart_mock.calls[2].request.body == file_content


def test_upload_with_workflows(multipart_mock):
    workflow_ids = ['workflow-id-1', 'workflow-id-2']
    store_params = {'workflows': workflow_ids}
    client = Client(APIKEY)
    filelink = client.upload(filepath='tests/data/bird.jpg', store_params=store_params)
    assert filelink.handle == HANDLE
    multipart_complete_payload = json.loads(multipart_mock.calls[3].request.body.decode())
    assert multipart_complete_payload['store']['workflows'] == workflow_ids


def test_upload_chunk(httpx_mock):
    httpx_mock.add_response(
        method='POST', url='https://fsuploads.com/multipart/upload',
        status_code=200, json={'url': 'http://s3-upload.url', 'headers': {}}
    )
    httpx_mock.add_response(method='PUT', url='http://s3-upload.url', headers={'ETag': 'etagX'})

    chunk = Chunk(num=123, seek_point=0, filepath='tests/data/doom.mp4')
    start_response = defaultdict(str)
    start_response['location_url'] = 'fsuploads.com'
    upload_result = upload_chunk('apikey', 'filename', 's3', start_response, chunk)
    assert upload_result == {'part_number': 123, 'etag': 'etagX'}
