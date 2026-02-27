### Explanation of Changes
To migrate the code from using the `requests` library to `httpx`, the following changes were made:
1. **Replace `responses` with `respx`:** The `responses` library is specifically designed for mocking `requests` calls. Since we are migrating to `httpx`, we replaced it with `respx`, which is designed for mocking `httpx` calls.
2. **Update Mocking Syntax:** The syntax for mocking requests in `respx` is slightly different from `responses`. For example:
   - `responses.add` is replaced with `respx.mock` and `respx.route`.
   - `responses.POST` and `responses.PUT` are replaced with `respx.post` and `respx.put`.
3. **Update HTTP Calls:** The `requests` library's HTTP methods (e.g., `requests.post`, `requests.put`) are replaced with their `httpx` equivalents (e.g., `httpx.post`, `httpx.put`).
4. **Session Management:** If `requests.Session` was used, it would be replaced with `httpx.Client`. However, the provided code does not use sessions, so no changes were needed in this regard.
5. **Mocking Headers and Body:** The way headers and body are accessed in `respx` is slightly different, so adjustments were made to ensure compatibility.

### Modified Code
Here is the complete code after migrating to `httpx`:

```python
import io
import json
from collections import defaultdict

import respx
import pytest
import httpx

from filestack import Client
from filestack import config
from filestack.uploads.multipart import upload_chunk, Chunk

APIKEY = 'APIKEY'
HANDLE = 'SOMEHANDLE'


@pytest.fixture
def multipart_mock():
    with respx.mock as mock:
        mock.post(config.MULTIPART_START_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    'region': 'us-east-1', 'upload_id': 'someuuid', 'uri': 'someuri',
                    'location_url': 'fs-uploads.com'
                }
            )
        )
        mock.post('https://fs-uploads.com/multipart/upload').mock(
            return_value=httpx.Response(
                200,
                json={'url': 'http://somewhere.on.s3', 'headers': {'filestack': 'header'}}
            )
        )
        mock.put('http://somewhere.on.s3').mock(
            return_value=httpx.Response(200, headers={'ETag': 'abc'})
        )
        mock.post('https://fs-uploads.com/multipart/complete').mock(
            return_value=httpx.Response(
                200,
                json={'url': 'https://cdn.filestackcontent.com/{}'.format(HANDLE), 'handle': HANDLE}
            )
        )
        yield mock


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
    assert multipart_mock.calls[2].request.content == file_content


def test_upload_with_workflows(multipart_mock):
    workflow_ids = ['workflow-id-1', 'workflow-id-2']
    store_params = {'workflows': workflow_ids}
    client = Client(APIKEY)
    filelink = client.upload(filepath='tests/data/bird.jpg', store_params=store_params)
    assert filelink.handle == HANDLE
    multipart_complete_payload = json.loads(multipart_mock.calls[3].request.content.decode())
    assert multipart_complete_payload['store']['workflows'] == workflow_ids


@respx.mock
def test_upload_chunk():
    respx.post('https://fsuploads.com/multipart/upload').mock(
        return_value=httpx.Response(
            200, json={'url': 'http://s3-upload.url', 'headers': {}}
        )
    )
    respx.put('http://s3-upload.url').mock(
        return_value=httpx.Response(200, headers={'ETag': 'etagX'})
    )

    chunk = Chunk(num=123, seek_point=0, filepath='tests/data/doom.mp4')
    start_response = defaultdict(str)
    start_response['location_url'] = 'fsuploads.com'
    upload_result = upload_chunk('apikey', 'filename', 's3', start_response, chunk)
    assert upload_result == {'part_number': 123, 'etag': 'etagX'}
```

### Key Points
- The `responses` library was replaced with `respx` for mocking HTTP requests.
- The `httpx` library was used for HTTP calls instead of `requests`.
- Mocking syntax and request/response handling were updated to align with `httpx` and `respx`.
- The overall structure and logic of the code remain unchanged to ensure compatibility with the rest of the application.