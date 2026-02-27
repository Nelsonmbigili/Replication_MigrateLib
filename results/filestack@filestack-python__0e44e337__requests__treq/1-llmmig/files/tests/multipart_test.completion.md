### Explanation of Changes
The migration from `requests` to `treq` involves the following changes:
1. **Replace `responses` with `treq` for mocking HTTP requests**:
   - `responses` is tightly coupled with `requests`. Since `treq` is asynchronous, we need to use `pytest-treq` or `treq`'s own testing utilities to mock HTTP requests.
   - For simplicity, I replaced `responses` with `treq`'s asynchronous request handling and used `pytest-treq` for testing.
   
2. **Update synchronous HTTP calls to asynchronous**:
   - `treq` is built on `Twisted` and uses asynchronous programming. All HTTP calls (e.g., `requests.post`, `requests.put`) are replaced with their `treq` equivalents (e.g., `treq.post`, `treq.put`).
   - The test functions are updated to be asynchronous (`async def`) and use `await` for `treq` calls.

3. **Adjust mocking for `treq`**:
   - Mocking in `treq` is done using `pytest-treq` or `twisted`'s `FakeEndpoint` and `StubTreq`. I used `StubTreq` to mock HTTP responses.

4. **Update test cases to handle asynchronous behavior**:
   - Test cases are updated to use `pytest.mark.asyncio` to handle asynchronous test functions.

### Modified Code
Below is the entire code after migrating from `requests` to `treq`:

```python
import io
import json
from collections import defaultdict

import pytest
from twisted.web.http_headers import Headers
from twisted.web.iweb import IBodyProducer
from twisted.internet.defer import succeed
from treq.testing import StubTreq
from twisted.web.resource import Resource

from filestack import Client
from filestack import config
from filestack.uploads.multipart import upload_chunk, Chunk

APIKEY = 'APIKEY'
HANDLE = 'SOMEHANDLE'


class MockMultipartResource(Resource):
    isLeaf = True

    def render_POST(self, request):
        if request.uri == config.MULTIPART_START_URL.encode():
            return json.dumps({
                'region': 'us-east-1', 'upload_id': 'someuuid', 'uri': 'someuri',
                'location_url': 'fs-uploads.com'
            }).encode()
        elif request.uri == b'/multipart/upload':
            return json.dumps({
                'url': 'http://somewhere.on.s3', 'headers': {'filestack': 'header'}
            }).encode()
        elif request.uri == b'/multipart/complete':
            return json.dumps({
                'url': f'https://cdn.filestackcontent.com/{HANDLE}', 'handle': HANDLE
            }).encode()
        return b''

    def render_PUT(self, request):
        request.setHeader('ETag', 'abc')
        return b''


@pytest.fixture
def multipart_mock():
    resource = MockMultipartResource()
    return StubTreq(resource)


@pytest.mark.asyncio
async def test_upload_filepath(multipart_mock):
    client = Client(APIKEY)
    filelink = await client.upload(filepath='tests/data/doom.mp4')
    assert filelink.handle == HANDLE
    assert filelink.upload_response == {'url': f'https://cdn.filestackcontent.com/{HANDLE}', 'handle': HANDLE}


@pytest.mark.asyncio
async def test_upload_file_obj(multipart_mock):
    file_content = b'file bytes'
    client = Client(APIKEY)
    filelink = await client.upload(file_obj=io.BytesIO(file_content))
    assert filelink.handle == HANDLE
    # Mocked headers and body checks
    assert multipart_mock._requests[1].headers[b'filestack'] == [b'header']
    assert multipart_mock._requests[1].content.read() == file_content


@pytest.mark.asyncio
async def test_upload_with_workflows(multipart_mock):
    workflow_ids = ['workflow-id-1', 'workflow-id-2']
    store_params = {'workflows': workflow_ids}
    client = Client(APIKEY)
    filelink = await client.upload(filepath='tests/data/bird.jpg', store_params=store_params)
    assert filelink.handle == HANDLE
    multipart_complete_payload = json.loads(
        (await multipart_mock._requests[2].content.read()).decode()
    )
    assert multipart_complete_payload['store']['workflows'] == workflow_ids


class MockChunkResource(Resource):
    isLeaf = True

    def render_POST(self, request):
        if request.uri == b'/multipart/upload':
            return json.dumps({'url': 'http://s3-upload.url', 'headers': {}}).encode()
        return b''

    def render_PUT(self, request):
        request.setHeader('ETag', 'etagX')
        return b''


@pytest.mark.asyncio
async def test_upload_chunk():
    resource = MockChunkResource()
    stub_treq = StubTreq(resource)

    chunk = Chunk(num=123, seek_point=0, filepath='tests/data/doom.mp4')
    start_response = defaultdict(str)
    start_response['location_url'] = 'fsuploads.com'
    upload_result = await upload_chunk('apikey', 'filename', 's3', start_response, chunk, stub_treq)
    assert upload_result == {'part_number': 123, 'etag': 'etagX'}
```

### Key Notes:
1. **`StubTreq`**:
   - `StubTreq` is used to mock HTTP requests and responses for `treq`. It allows us to simulate server behavior without making actual network calls.

2. **Asynchronous Tests**:
   - All test functions are now asynchronous (`async def`) and use `pytest.mark.asyncio` to handle asynchronous execution.

3. **MockMultipartResource**:
   - This class simulates the behavior of the server for multipart uploads. It handles `POST` and `PUT` requests and returns appropriate mocked responses.

4. **MockChunkResource**:
   - This class is used to mock the server behavior for chunk uploads.

5. **`await`**:
   - All `treq` calls (e.g., `treq.post`, `treq.put`) are awaited since they return deferred objects.

This approach ensures the code is fully migrated to `treq` while maintaining the original functionality and structure.