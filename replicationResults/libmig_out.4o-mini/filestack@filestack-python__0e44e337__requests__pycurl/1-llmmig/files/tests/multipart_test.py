import io
import json
from collections import defaultdict
import pycurl
from io import BytesIO
import pytest

from filestack import Client
from filestack import config
from filestack.uploads.multipart import upload_chunk, Chunk

APIKEY = 'APIKEY'
HANDLE = 'SOMEHANDLE'


@pytest.fixture
def multipart_mock():
    # Mocking responses using pycurl
    class MockCurl:
        def __init__(self):
            self.response_body = BytesIO()
            self.response_code = 200

        def perform(self):
            pass

        def setopt(self, option, value):
            if option == pycurl.WRITEFUNCTION:
                self.write_function = value
            elif option == pycurl.URL:
                self.url = value
            elif option == pycurl.HTTPHEADER:
                self.headers = value
            elif option == pycurl.CUSTOMREQUEST:
                self.custom_request = value
            elif option == pycurl.POSTFIELDS:
                self.postfields = value

        def getinfo(self, info):
            if info == pycurl.RESPONSE_CODE:
                return self.response_code
            return None

        def close(self):
            pass

    mock_curl = MockCurl()
    yield mock_curl


def test_upload_filepath(multipart_mock):
    client = Client(APIKEY)
    filelink = client.upload(filepath='tests/data/doom.mp4')
    assert filelink.handle == HANDLE
    assert filelink.upload_response == {'url': 'https://cdn.filestackcontent.com/{}'.format(HANDLE), 'handle': HANDLE}


def test_upload_file_obj(multipart_mock):
    file_content = b'file bytes'
    filelink = Client(APIKEY).upload(file_obj=io.BytesIO(file_content))
    assert filelink.handle == HANDLE
    assert multipart_mock.headers[2]['filestack'] == 'header'
    assert multipart_mock.postfields == file_content


def test_upload_with_workflows(multipart_mock):
    workflow_ids = ['workflow-id-1', 'workflow-id-2']
    store_params = {'workflows': workflow_ids}
    client = Client(APIKEY)
    filelink = client.upload(filepath='tests/data/bird.jpg', store_params=store_params)
    assert filelink.handle == HANDLE
    multipart_complete_payload = json.loads(multipart_mock.postfields.decode())
    assert multipart_complete_payload['store']['workflows'] == workflow_ids


@responses.activate
def test_upload_chunk():
    # Mocking responses using pycurl
    class MockCurl:
        def __init__(self):
            self.response_body = BytesIO()
            self.response_code = 200

        def perform(self):
            pass

        def setopt(self, option, value):
            if option == pycurl.WRITEFUNCTION:
                self.write_function = value
            elif option == pycurl.URL:
                self.url = value
            elif option == pycurl.HTTPHEADER:
                self.headers = value
            elif option == pycurl.CUSTOMREQUEST:
                self.custom_request = value
            elif option == pycurl.POSTFIELDS:
                self.postfields = value

        def getinfo(self, info):
            if info == pycurl.RESPONSE_CODE:
                return self.response_code
            return None

        def close(self):
            pass

    mock_curl = MockCurl()
    chunk = Chunk(num=123, seek_point=0, filepath='tests/data/doom.mp4')
    start_response = defaultdict(str)
    start_response['location_url'] = 'fsuploads.com'
    upload_result = upload_chunk('apikey', 'filename', 's3', start_response, chunk)
    assert upload_result == {'part_number': 123, 'etag': 'etagX'}
