### Explanation of Changes

To migrate the code from using the `requests` library to `pycurl`, the following changes were made:

1. **Replace `requests` with `pycurl`**:
   - `pycurl` is a lower-level library compared to `requests`, so it requires more manual setup for HTTP requests.
   - Each HTTP request (e.g., `POST`, `PUT`) is implemented using `pycurl.Curl` objects, where we configure the URL, HTTP method, headers, and body explicitly.

2. **Mocking HTTP Requests**:
   - The `responses` library is used to mock HTTP requests in the original code. However, `responses` is designed to work with `requests` and does not support `pycurl`.
   - To handle this, I replaced `responses` with a custom mocking mechanism using `http.server` to simulate HTTP endpoints.

3. **Handling HTTP Headers and Body**:
   - In `pycurl`, headers and body data must be set explicitly using options like `HTTPHEADER` and `POSTFIELDS`.
   - For file uploads, `pycurl` requires the use of `FORM` for multipart data.

4. **Reading Responses**:
   - `pycurl` writes responses to a buffer, which must be read and parsed manually.

5. **Test Adjustments**:
   - The tests were updated to use the custom HTTP server for mocking instead of `responses`.

Below is the modified code.

---

### Modified Code

```python
import io
import json
from collections import defaultdict
import pytest
import pycurl
from io import BytesIO
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

from filestack import Client
from filestack import config
from filestack.uploads.multipart import upload_chunk, Chunk

APIKEY = 'APIKEY'
HANDLE = 'SOMEHANDLE'


class MockServerRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == config.MULTIPART_START_URL:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'region': 'us-east-1', 'upload_id': 'someuuid', 'uri': 'someuri',
                'location_url': 'fs-uploads.com'
            }).encode())
        elif self.path == '/multipart/upload':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'url': 'http://somewhere.on.s3', 'headers': {'filestack': 'header'}
            }).encode())
        elif self.path == '/multipart/complete':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'url': f'https://cdn.filestackcontent.com/{HANDLE}', 'handle': HANDLE
            }).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_PUT(self):
        if self.path == 'http://somewhere.on.s3':
            self.send_response(200)
            self.send_header('ETag', 'abc')
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()


@pytest.fixture(scope="module")
def mock_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, MockServerRequestHandler)
    thread = Thread(target=httpd.serve_forever)
    thread.setDaemon(True)
    thread.start()
    yield
    httpd.shutdown()


def make_request(url, method='GET', headers=None, body=None):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    if method == 'POST':
        c.setopt(c.POST, 1)
        if body:
            c.setopt(c.POSTFIELDS, body)
    elif method == 'PUT':
        c.setopt(c.CUSTOMREQUEST, 'PUT')
        if body:
            c.setopt(c.POSTFIELDS, body)
    if headers:
        c.setopt(c.HTTPHEADER, [f"{k}: {v}" for k, v in headers.items()])
    c.perform()
    c.close()
    return buffer.getvalue().decode()


def test_upload_filepath(mock_server):
    client = Client(APIKEY)
    filelink = client.upload(filepath='tests/data/doom.mp4')
    assert filelink.handle == HANDLE
    assert filelink.upload_response == {'url': f'https://cdn.filestackcontent.com/{HANDLE}', 'handle': HANDLE}


def test_upload_file_obj(mock_server):
    file_content = b'file bytes'
    filelink = Client(APIKEY).upload(file_obj=io.BytesIO(file_content))
    assert filelink.handle == HANDLE


def test_upload_with_workflows(mock_server):
    workflow_ids = ['workflow-id-1', 'workflow-id-2']
    store_params = {'workflows': workflow_ids}
    client = Client(APIKEY)
    filelink = client.upload(filepath='tests/data/bird.jpg', store_params=store_params)
    assert filelink.handle == HANDLE


def test_upload_chunk(mock_server):
    chunk = Chunk(num=123, seek_point=0, filepath='tests/data/doom.mp4')
    start_response = defaultdict(str)
    start_response['location_url'] = 'fsuploads.com'
    upload_result = upload_chunk('apikey', 'filename', 's3', start_response, chunk)
    assert upload_result == {'part_number': 123, 'etag': 'etagX'}
```

---

### Key Notes:
- The `responses` library was replaced with a custom HTTP server (`MockServerRequestHandler`) to mock HTTP endpoints.
- The `make_request` function wraps `pycurl` to handle HTTP requests.
- The rest of the code remains unchanged, adhering to the original structure and logic.