### Explanation of Changes

To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Import Statement**: The import statement for `requests` was replaced with `urllib3`. 
2. **Creating a Pool Manager**: A `PoolManager` instance was created to handle HTTP connections.
3. **Making Requests**: The `requests.post` and `requests.put` methods were replaced with the `urlopen` method of the `PoolManager` instance. The data for POST requests was encoded as JSON using `json.dumps()` and passed as bytes.
4. **Handling Responses**: The response from the `urlopen` method is read using `.data` and decoded from bytes to a string. The JSON response is then parsed using `json.loads()`.

Here is the modified code:

```python
import os
import hashlib
import mimetypes
import multiprocessing
from base64 import b64encode
from functools import partial
from concurrent.futures import ThreadPoolExecutor
import json
import urllib3

from filestack import config

http = urllib3.PoolManager()

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


def multipart_request(url, payload, params=None, security=None):
    for key in ('path', 'location', 'region', 'container', 'access'):
        if key in params:
            payload['store'][key] = params[key]

    if security:
        payload.update({
            'policy': security.policy_b64,
            'signature': security.signature
        })

    response = http.request('POST', url, body=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
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

    fs_resp = multipart_request(
        'https://{}/multipart/upload'.format(start_response['location_url']),
        payload
    )

    resp = http.request('PUT', fs_resp['url'], headers=fs_resp['headers'], body=chunk.bytes)

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

    complete_url = 'https://{}/multipart/complete'.format(location_url)
    complete_response = multipart_request(complete_url, payload, params, security)
    return complete_response
```