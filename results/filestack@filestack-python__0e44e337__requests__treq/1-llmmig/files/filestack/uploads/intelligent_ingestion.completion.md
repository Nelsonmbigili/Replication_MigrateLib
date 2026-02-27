### Explanation of Changes
The migration from `requests` to `treq` involves the following key changes:
1. **Asynchronous Nature of `treq`**: `treq` is built on top of `Twisted` and is asynchronous. Therefore, all `requests` calls (e.g., `requests.post`, `requests.put`, etc.) are replaced with their asynchronous counterparts from `treq` (e.g., `treq.post`, `treq.put`, etc.).
2. **Awaiting Responses**: Since `treq` returns `Deferred` objects, we need to use `await` to get the actual response. This requires making the functions asynchronous (`async def`).
3. **Session Management**: `treq` does not use `requests.Session`. Instead, it uses `treq`'s built-in session management.
4. **Response Handling**: `treq` provides methods like `response.json()` and `response.text()` as coroutines, so we need to `await` them to get the response content.
5. **Retries**: `treq` does not have built-in retry functionality like `requests.adapters.HTTPAdapter`. You would need to implement retries manually or use an external library for retries.

Below is the modified code.

---

### Modified Code
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
from base64 import b64encode
from concurrent.futures import ThreadPoolExecutor

import treq
from twisted.internet.defer import ensureDeferred

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


async def upload_part(apikey, filename, filepath, filesize, storage, start_response, part):
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
            api_resp = await treq.post(url, json=payload)
            api_resp_json = await api_resp.json()
            s3_resp = await treq.put(api_resp_json['url'], headers=api_resp_json['headers'], data=chunk_data)
            if s3_resp.code != 200:
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
    await treq.post(url, json=payload)


async def upload(apikey, filepath, file_obj, storage, params=None, security=None):
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

    start_response = await treq.post(config.MULTIPART_START_URL, json=payload)
    start_response_json = await start_response.json()
    parts = [
        {
            'seek_point': seek_point,
            'num': num + 1
        } for num, seek_point in enumerate(range(0, filesize, DEFAULT_PART_SIZE))
    ]

    fii_upload = functools.partial(
        upload_part, apikey, filename, filepath, filesize, storage, start_response_json
    )

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        await ensureDeferred(executor.map(fii_upload, parts))

    payload.update({
        'uri': start_response_json['uri'],
        'region': start_response_json['region'],
        'upload_id': start_response_json['upload_id'],
    })

    if 'workflows' in params:
        payload['store']['workflows'] = params.pop('workflows')

    if 'upload_tags' in params:
        payload['upload_tags'] = params.pop('upload_tags')

    complete_url = 'https://{}/multipart/complete'.format(start_response_json['location_url'])
    response = await treq.post(complete_url, json=payload, headers=config.HEADERS)
    if response.code != 200:
        response_content = await response.text()
        log.error('Did not receive a correct complete response: %s. Content %s', response, response_content)
        raise Exception('Invalid complete response: {}'.format(response_content))

    return await response.json()
```

---

### Key Notes
1. **Asynchronous Execution**: The `upload` and `upload_part` functions are now asynchronous (`async def`), and all `treq` calls are awaited.
2. **ThreadPoolExecutor**: Since `treq` is asynchronous, we use `ensureDeferred` to handle the `ThreadPoolExecutor` properly.
3. **Error Handling**: Error handling remains the same, but now we await the response content when logging errors.
4. **Retries**: The retry logic from `requests.adapters.HTTPAdapter` is not directly available in `treq`. If retries are critical, you can implement them manually or use a library like `tenacity`.