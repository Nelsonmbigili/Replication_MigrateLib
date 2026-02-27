import io
import json
from collections import defaultdict

import urllib3_mock
import pytest

from filestack import Client
from filestack import config
from filestack.uploads.multipart import upload_chunk, Chunk

APIKEY = 'APIKEY'
HANDLE = 'SOMEHANDLE'


@pytest.fixture
def multipart_mock():
    with urllib3_mock.PoolManager() as http:
        http.request(
            'POST', config.MULTIPART_START_URL,
            headers={'Content-Type': 'application/json'},
            body=json.dumps({
                'region': 'us-east-1', 'upload_id': 'someuuid', 'uri': 'someuri',
                'location_url': 'fs-uploads.com'
            }).encode('utf-8'),
            preload_content=False,
            status=200
        )
        http.request(
            'POST', 'https://fs-uploads.com/multipart/upload',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'url': 'http://somewhere.on.s3', 'headers': {'filestack': 'header'}}).encode('utf-8'),
            preload_content=False,
            status=200
        )
        http.request(
            'PUT', 'http://somewhere.on.s3',
            headers={'ETag': 'abc'},
            body=b'',
            preload_content=False,
            status=200
        )
        http.request(
            'POST', 'https://fs-uploads.com/multipart/complete',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'url': 'https://cdn.filestackcontent.com/{}'.format(HANDLE), 'handle': HANDLE}).encode('utf-8'),
            preload_content=False,
            status=200
        )
        yield http


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


@urllib3_mock.activate
def test_upload_chunk():
    http = urllib3_mock.PoolManager()
    http.request(
        'POST', 'https://fsuploads.com/multipart/upload',
        headers={'Content-Type': 'application/json'},
        body=json.dumps({'url': 'http://s3-upload.url', 'headers': {}}).encode('utf-8'),
        preload_content=False,
        status=200
    )
    http.request(
        'PUT', 'http://s3-upload.url',
        headers={'ETag': 'etagX'},
        body=b'',
        preload_content=False,
        status=200
    )

    chunk = Chunk(num=123, seek_point=0, filepath='tests/data/doom.mp4')
    start_response = defaultdict(str)
    start_response['location_url'] = 'fsuploads.com'
    upload_result = upload_chunk('apikey', 'filename', 's3', start_response, chunk)
    assert upload_result == {'part_number': 123, 'etag': 'etagX'}
