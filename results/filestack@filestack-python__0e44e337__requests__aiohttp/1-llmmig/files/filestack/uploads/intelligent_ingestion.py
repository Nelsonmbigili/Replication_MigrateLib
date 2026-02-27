import io
import os
import sys
import mimetypes
import multiprocessing
import hashlib
import logging
import functools
import threading
import asyncio
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

    async with aiohttp.ClientSession() as session:
        while chunk_data:
            payload = payload_base.copy()
            payload.update({
                'size': len(chunk_data),
                'md5': b64encode(hashlib.md5(chunk_data).digest()).strip().decode('utf-8'),
                'offset': offset,
                'fii': True
            })

            try:
                url = f'https://{start_response["location_url"]}/multipart/upload'
                async with session.post(url, json=payload) as api_resp:
                    api_resp_data = await api_resp.json()

                async with session.put(api_resp_data['url'], headers=api_resp_data['headers'], data=chunk_data) as s3_resp:
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

        url = f'https://{start_response["location_url"]}/multipart/commit'
        async with session.post(url, json=payload) as commit_resp:
            if commit_resp.status != 200:
                log.error('Commit failed: %s', await commit_resp.text())
                raise Exception('Commit failed')


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

    async with aiohttp.ClientSession() as session:
        async with session.post(config.MULTIPART_START_URL, json=payload) as start_resp:
            start_response = await start_resp.json()

        parts = [
            {
                'seek_point': seek_point,
                'num': num + 1
            } for num, seek_point in enumerate(range(0, filesize, DEFAULT_PART_SIZE))
        ]

        fii_upload = functools.partial(
            upload_part, apikey, filename, filepath, filesize, storage, start_response
        )

        await asyncio.gather(*(fii_upload(part) for part in parts))

        payload.update({
            'uri': start_response['uri'],
            'region': start_response['region'],
            'upload_id': start_response['upload_id'],
        })

        if 'workflows' in params:
            payload['store']['workflows'] = params.pop('workflows')

        if 'upload_tags' in params:
            payload['upload_tags'] = params.pop('upload_tags')

        complete_url = f'https://{start_response["location_url"]}/multipart/complete'
        async with session.post(complete_url, json=payload, headers=config.HEADERS) as response:
            if response.status != 200:
                log.error('Did not receive a correct complete response: %s. Content %s', response, await response.text())
                raise Exception('Invalid complete response: {}'.format(await response.text()))

            return await response.json()
