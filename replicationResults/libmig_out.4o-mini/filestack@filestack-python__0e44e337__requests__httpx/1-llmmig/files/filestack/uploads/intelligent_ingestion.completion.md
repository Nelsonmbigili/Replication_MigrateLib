### Explanation of Changes

To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:

1. **Import Statement**: Changed the import statement from `from filestack.utils import requests` to `import httpx`.
2. **Session Management**: The `requests.Session()` was replaced with `httpx.Client()`, which is the equivalent in `httpx`.
3. **Method Calls**: The method calls for `post` and `put` were updated to use the `httpx` syntax. The `json` parameter is still used in the same way, but the response handling is slightly different.
4. **Response Handling**: The response from `httpx` does not have a `.json()` method directly on the response object. Instead, we use `response.json()` to get the JSON data.
5. **Error Handling**: The error handling remains the same, but we ensure that the response checks are compatible with `httpx`.

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
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor

from base64 import b64encode

import httpx

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
            async with httpx.AsyncClient() as client:
                api_resp = await client.post(url, json=payload)
                api_resp = api_resp.json()
                s3_resp = await client.put(api_resp['url'], headers=api_resp['headers'], data=chunk_data)
                if not s3_resp.is_success:
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
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)


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

    async with httpx.AsyncClient() as client:
        start_response = await client.post(config.MULTIPART_START_URL, json=payload)
        start_response = start_response.json()
    
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
    async with httpx.AsyncClient() as client:
        response = await client.post(complete_url, json=payload, headers=config.HEADERS)
        if response.status_code != 200:
            log.error('Did not receive a correct complete response: %s. Content %s', response, response.content)
            raise Exception('Invalid complete response: {}'.format(response.content))

    return response.json()
```

### Note
The code above assumes that the `upload_part` and `upload` functions are called in an asynchronous context, as `httpx` supports asynchronous requests. If the original code was synchronous, you would need to adjust the usage of `httpx` accordingly.