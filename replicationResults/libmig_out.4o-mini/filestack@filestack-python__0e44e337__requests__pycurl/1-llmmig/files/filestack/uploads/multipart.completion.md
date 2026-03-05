### Explanation of Changes

To migrate the code from using the `requests` library to the `pycurl` library, several key changes were made:

1. **Import Statement**: The import for `requests` was replaced with `pycurl`.
2. **HTTP Requests**: The `requests.post` and `requests.put` methods were replaced with `pycurl` methods. This involved setting up a `pycurl.Curl` object, configuring it with the appropriate options, and performing the request.
3. **Handling JSON**: Since `pycurl` does not handle JSON serialization/deserialization automatically, we manually converted the payload to JSON using the `json` module and set the appropriate headers.
4. **Response Handling**: The response from `pycurl` is handled differently. We read the response data from a buffer instead of directly calling `.json()`.

Here is the modified code:

```python
import os
import hashlib
import mimetypes
import multiprocessing
from base64 import b64encode
from functools import partial
from concurrent.futures import ThreadPoolExecutor
import pycurl
import json
from io import BytesIO

from filestack import config


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

    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.POSTFIELDS, json.dumps(payload))
    c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()

    response_data = buffer.getvalue()
    return json.loads(response_data)


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

    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, fs_resp['url'])
    c.setopt(c.PUT, 1)
    c.setopt(c.HTTPHEADER, fs_resp['headers'])
    c.setopt(c.READDATA, BytesIO(chunk.bytes))
    c.setopt(c.INFILESIZE, len(chunk.bytes))
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()

    response_data = buffer.getvalue()
    return {'part_number': chunk.num, 'etag': fs_resp['etag']}


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

This code now uses `pycurl` for HTTP requests while maintaining the original structure and functionality of the application.