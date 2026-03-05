### Explanation of Changes

To migrate the code from using the `requests` library to the `urllib3` library, several key changes were made:

1. **Importing `urllib3`**: The `requests` library was replaced with `urllib3`. The `requests` import statement was removed, and `urllib3` was imported instead.

2. **Creating a Pool Manager**: Instead of using a `Session` object from `requests`, a `PoolManager` from `urllib3` was created to handle connections.

3. **Making HTTP Requests**: The `requests.post` and `requests.put` methods were replaced with `http.request('POST', ...)` and `http.request('PUT', ...)` respectively. The payload was converted to JSON using `json.dumps()` and the headers were passed as a dictionary.

4. **Handling Responses**: The response handling was adjusted to work with `urllib3`'s response object, which does not have a `.json()` method. Instead, the response data was read and parsed using `json.loads()`.

5. **Error Handling**: The error handling was adjusted to check the status of the response using `response.status` instead of `response.ok`.

Here is the modified code:

```python
import io
import os
import sys
import mimetypes
import multiprocessing
import hashlib
import logging
import functools
import threading
import json
import urllib3
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor

from base64 import b64encode

from filestack import config

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(asctime)s - %(processName)s[%(process)d] - %(levelname)s - %(message)s"))
log.addHandler(handler)

MB = 1024 ** 2
DEFAULT_PART_SIZE = 8 * MB
CHUNK_SIZE = 8 * MB
MIN_CHUNK_SIZE = 32 * 1024
MAX_DELAY = 4
NUM_THREADS = multiprocessing.cpu_count()

lock = threading.Lock()

http = urllib3.PoolManager()

def decrease_chunk_size():
    global CHUNK_SIZE
    CHUNK_SIZE //= 2
    if CHUNK_SIZE < MIN_CHUNK_SIZE:
        raise Exception('Minimal chunk size failed')

def upload_part(apikey, filename, filepath, filesize, storage, start_response, part):
    with open(filepath, 'rb') as f:
        f.seek(part['seek_point'])
        part_bytes = io.BytesIO(f.read(DEFAULT_PART_SIZE))

    payload_base = {
        'apikey': apikey,
        'uri': start_response['uri'],
        'region': start_response['region'],
        'upload_id': start_response['upload_id'],
        'store': {'location': storage},
        'part': part['num']
    }

    global CHUNK_SIZE
    chunk_data = part_bytes.read(CHUNK_SIZE)
    offset = 0

    while chunk_data:
        payload = payload_base.copy()
        payload.update({
            'size': len(chunk_data),
            'md5': b64encode(hashlib.md5(chunk_data).digest()).strip().decode('utf-8'),
            'offset': offset,
            'fii': True
        })

        try:
            url = 'https://{}/multipart/upload'.format(start_response['location_url'])
            response = http.request('POST', url, body=json.dumps(payload), headers={'Content-Type': 'application/json'})
            api_resp = json.loads(response.data.decode('utf-8'))
            s3_resp = http.request('PUT', api_resp['url'], headers=api_resp['headers'], body=chunk_data)
            if s3_resp.status != 200:
                raise Exception('Incorrect S3 response')
            offset += len(chunk_data)
            chunk_data = part_bytes.read(CHUNK_SIZE)
        except Exception as e:
            log.error('Upload failed: %s', str(e))
            with lock:
                if CHUNK_SIZE >= len(chunk_data):
                    decrease_chunk_size()

            part_bytes.seek(offset)
            chunk_data = part_bytes.read(CHUNK_SIZE)

    payload = payload_base.copy()
    payload.update({'size': filesize})

    url = 'https://{}/multipart/commit'.format(start_response['location_url'])
    http.request('POST', url, body=json.dumps(payload), headers={'Content-Type': 'application/json'})

def upload(apikey, filepath, file_obj, storage, params=None, security=None):
    params = params or {}

    filename = params.get('filename') or os.path.split(filepath)[1]
    mimetype = params.get('mimetype') or mimetypes.guess_type(filepath)[0] or config.DEFAULT_UPLOAD_MIMETYPE
    filesize = os.path.getsize(filepath)

    payload = {
        'apikey': apikey,
        'filename': filename,
        'mimetype': mimetype,
        'size': filesize,
        'fii': True,
        'store': {
            'location': storage
        }
    }

    for key in ('path', 'location', 'region', 'container', 'access'):
        if key in params:
            payload['store'][key] = params[key]

    if security:
        payload.update({
            'policy': security.policy_b64,
            'signature': security.signature
        })

    start_response = http.request('POST', config.MULTIPART_START_URL, body=json.dumps(payload), headers={'Content-Type': 'application/json'})
    start_response = json.loads(start_response.data.decode('utf-8'))
    parts = [
        {
            'seek_point': seek_point,
            'num': num + 1
        } for num, seek_point in enumerate(range(0, filesize, DEFAULT_PART_SIZE))
    ]

    fii_upload = functools.partial(
        upload_part, apikey, filename, filepath, filesize, storage, start_response
    )

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        list(executor.map(fii_upload, parts))

    payload.update({
        'uri': start_response['uri'],
        'region': start_response['region'],
        'upload_id': start_response['upload_id'],
    })

    if 'workflows' in params:
        payload['store']['workflows'] = params.pop('workflows')

    if 'upload_tags' in params:
        payload['upload_tags'] = params.pop('upload_tags')

    complete_url = 'https://{}/multipart/complete'.format(start_response['location_url'])
    response = http.request('POST', complete_url, body=json.dumps(payload), headers={'Content-Type': 'application/json'})
    if response.status != 200:
        log.error('Did not receive a correct complete response: %s. Content %s', response, response.data)
        raise Exception('Invalid complete response: {}'.format(response.data))

    return json.loads(response.data.decode('utf-8'))
```