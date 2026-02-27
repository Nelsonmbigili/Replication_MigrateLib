### Explanation of Changes
The migration from the `requests` library to `urllib3` involves replacing all `requests`-specific methods (e.g., `requests.post`, `requests.put`) with equivalent functionality using `urllib3`. The key changes include:
1. **HTTP Connection Management**: `urllib3` requires an explicit `PoolManager` to manage HTTP connections.
2. **POST Requests**: Replaced `requests.post` with `urllib3.PoolManager.request` using the `method='POST'` argument.
3. **PUT Requests**: Replaced `requests.put` with `urllib3.PoolManager.request` using the `method='PUT'` argument.
4. **JSON Handling**: `urllib3` does not have built-in JSON handling like `requests`. Therefore, JSON payloads are serialized using the `json.dumps` method, and responses are deserialized using `json.loads`.
5. **Headers**: Headers are passed explicitly in `urllib3` requests.
6. **Response Handling**: `urllib3` responses are handled differently. The response body is accessed via `response.data`, and headers are accessed via `response.headers`.

Below is the modified code.

---

### Modified Code
```python
import os
import hashlib
import mimetypes
import multiprocessing
import json
from base64 import b64encode
from functools import partial
from concurrent.futures import ThreadPoolExecutor

from filestack import config
from urllib3 import PoolManager


class Chunk:
    def __init__(self, num, seek_point, data=None, filepath=None):
        self.num = num
        self.seek_point = seek_point
        self.data = data
        self.filepath = filepath

    def __repr__(self):
        return '<Chunk part: {}, seek: {}>'.format(self.num, self.seek_point)

    @property
    def bytes(self):
        if self.data:
            return self.data

        with open(self.filepath, 'rb') as f:
            f.seek(self.seek_point)
            data = f.read(config.DEFAULT_CHUNK_SIZE)

        return data


# Initialize a PoolManager for HTTP connections
http = PoolManager()


def multipart_request(url, payload, params=None, security=None):
    for key in ('path', 'location', 'region', 'container', 'access'):
        if key in params:
            payload['store'][key] = params[key]

    if security:
        payload.update({
            'policy': security.policy_b64,
            'signature': security.signature
        })

    # Serialize payload to JSON
    encoded_payload = json.dumps(payload).encode('utf-8')

    # Make a POST request
    response = http.request(
        'POST',
        url,
        body=encoded_payload,
        headers={'Content-Type': 'application/json'}
    )

    # Deserialize the JSON response
    return json.loads(response.data.decode('utf-8'))


def make_chunks(filepath=None, file_obj=None, filesize=None):
    chunks = []
    for num, seek_point in enumerate(range(0, filesize, config.DEFAULT_CHUNK_SIZE)):
        if filepath:
            chunks.append(Chunk(num + 1, seek_point, filepath=filepath))
        else:  # file_obj
            file_obj.seek(seek_point)
            chunks.append(Chunk(num + 1, seek_point, data=file_obj.read(config.DEFAULT_CHUNK_SIZE)))

    if file_obj:
        del file_obj

    return chunks


def upload_chunk(apikey, filename, storage, start_response, chunk):
    payload = {
        'apikey': apikey,
        'part': chunk.num,
        'size': len(chunk.bytes),
        'md5': b64encode(hashlib.md5(chunk.bytes).digest()).strip().decode('utf-8'),
        'uri': start_response['uri'],
        'region': start_response['region'],
        'upload_id': start_response['upload_id'],
        'store': {
            'location': storage,
        }
    }

    # Serialize payload to JSON
    encoded_payload = json.dumps(payload).encode('utf-8')

    # Make a POST request to get the upload URL and headers
    fs_resp = http.request(
        'POST',
        'https://{}/multipart/upload'.format(start_response['location_url']),
        body=encoded_payload,
        headers={'Content-Type': 'application/json'}
    )

    # Deserialize the JSON response
    fs_resp_data = json.loads(fs_resp.data.decode('utf-8'))

    # Make a PUT request to upload the chunk
    resp = http.request(
        'PUT',
        fs_resp_data['url'],
        body=chunk.bytes,
        headers=fs_resp_data['headers']
    )

    return {'part_number': chunk.num, 'etag': resp.headers['ETag']}


def multipart_upload(apikey, filepath, file_obj, storage, params=None, security=None):
    params = params or {}

    upload_processes = multiprocessing.cpu_count()

    if filepath:
        filename = params.get('filename') or os.path.split(filepath)[1]
        mimetype = params.get('mimetype') or mimetypes.guess_type(filepath)[0] or config.DEFAULT_UPLOAD_MIMETYPE
        filesize = os.path.getsize(filepath)
    else:
        filename = params.get('filename', 'unnamed_file')
        mimetype = params.get('mimetype') or config.DEFAULT_UPLOAD_MIMETYPE
        file_obj.seek(0, os.SEEK_END)
        filesize = file_obj.tell()

    payload = {
        'apikey': apikey,
        'filename': filename,
        'mimetype': mimetype,
        'size': filesize,
        'store': {
            'location': storage
        }
    }

    chunks = make_chunks(filepath, file_obj, filesize)
    start_response = multipart_request(config.MULTIPART_START_URL, payload, params, security)
    upload_func = partial(upload_chunk, apikey, filename, storage, start_response)

    with ThreadPoolExecutor(max_workers=upload_processes) as executor:
        uploaded_parts = list(executor.map(upload_func, chunks))

    location_url = start_response.pop('location_url')
    payload.update(start_response)
    payload['parts'] = uploaded_parts

    if 'workflows' in params:
        payload['store']['workflows'] = params.pop('workflows')

    if 'upload_tags' in params:
        payload['upload_tags'] = params.pop('upload_tags')

    # Serialize payload to JSON
    encoded_payload = json.dumps(payload).encode('utf-8')

    # Make a POST request to complete the upload
    complete_url = 'https://{}/multipart/complete'.format(location_url)
    complete_response = http.request(
        'POST',
        complete_url,
        body=encoded_payload,
        headers={'Content-Type': 'application/json'}
    )

    # Deserialize the JSON response
    return json.loads(complete_response.data.decode('utf-8'))
```

---

### Summary of Changes
- Replaced `requests.post` and `requests.put` with `http.request` from `urllib3`.
- Used `json.dumps` to serialize JSON payloads and `json.loads` to parse JSON responses.
- Explicitly passed headers for `Content-Type` and other required fields.
- Accessed response data using `response.data` and headers using `response.headers`.