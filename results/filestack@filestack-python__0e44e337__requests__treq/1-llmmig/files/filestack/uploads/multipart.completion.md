### Explanation of Changes
The migration from `requests` to `treq` involves the following changes:
1. **Importing `treq`**: Replace the `requests` import with `treq`.
2. **Asynchronous Nature of `treq`**: Since `treq` is asynchronous, all functions that use `treq` must be converted to `async` functions. This includes:
   - `multipart_request`
   - `upload_chunk`
   - `multipart_upload`
3. **Awaiting `treq` Calls**: Replace synchronous `requests.post` and `requests.put` calls with their `treq` equivalents (`treq.post` and `treq.put`) and use `await` to handle the asynchronous nature of `treq`.
4. **Handling JSON Responses**: Use `await response.json()` to parse JSON responses from `treq` calls.
5. **Concurrency**: Replace `ThreadPoolExecutor` with `asyncio.gather` for handling concurrent uploads, as `treq` is asynchronous and works well with `asyncio`.

### Modified Code
Here is the entire code after migrating to `treq`:

```python
import os
import hashlib
import mimetypes
import asyncio
from base64 import b64encode
from functools import partial

import treq

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


async def multipart_request(url, payload, params=None, security=None):
    for key in ('path', 'location', 'region', 'container', 'access'):
        if key in params:
            payload['store'][key] = params[key]

    if security:
        payload.update({
            'policy': security.policy_b64,
            'signature': security.signature
        })

    response = await treq.post(url, json=payload)
    return await response.json()


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


async def upload_chunk(apikey, filename, storage, start_response, chunk):
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

    fs_resp = await treq.post(
        'https://{}/multipart/upload'.format(start_response['location_url']),
        json=payload
    )
    fs_resp_json = await fs_resp.json()

    resp = await treq.put(fs_resp_json['url'], headers=fs_resp_json['headers'], data=chunk.bytes)
    return {'part_number': chunk.num, 'etag': resp.headers.getRawHeaders('ETag')[0]}


async def multipart_upload(apikey, filepath, file_obj, storage, params=None, security=None):
    params = params or {}

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
    start_response = await multipart_request(config.MULTIPART_START_URL, payload, params, security)
    upload_func = partial(upload_chunk, apikey, filename, storage, start_response)

    # Use asyncio.gather to upload chunks concurrently
    uploaded_parts = await asyncio.gather(*(upload_func(chunk) for chunk in chunks))

    location_url = start_response.pop('location_url')
    payload.update(start_response)
    payload['parts'] = uploaded_parts

    if 'workflows' in params:
        payload['store']['workflows'] = params.pop('workflows')

    if 'upload_tags' in params:
        payload['upload_tags'] = params.pop('upload_tags')

    complete_url = 'https://{}/multipart/complete'.format(location_url)
    complete_response = await multipart_request(complete_url, payload, params, security)
    return complete_response
```

### Key Notes:
1. **Concurrency**: `asyncio.gather` is used to handle concurrent uploads of chunks, replacing `ThreadPoolExecutor`.
2. **Headers Handling**: `treq` uses `twisted`'s `Headers` object, so `resp.headers.getRawHeaders('ETag')[0]` is used to extract the `ETag` header.
3. **Asynchronous Functions**: All functions that interact with `treq` are now `async` functions, and their calls must be awaited.