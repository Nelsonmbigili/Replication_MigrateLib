import io
import os
import sys
import mimetypes
import multiprocessing
import hashlib
import logging
import functools
import threading
import pycurl
import json
import time
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


def pycurl_post(url, payload, headers=None):
    """Helper function to perform a POST request using pycurl."""
    buffer = io.BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.POST, 1)
    c.setopt(c.POSTFIELDS, json.dumps(payload))
    c.setopt(c.WRITEDATA, buffer)
    if headers:
        c.setopt(c.HTTPHEADER, headers)
    c.perform()
    c.close()
    return buffer.getvalue().decode('utf-8')


def pycurl_put(url, data, headers=None):
    """Helper function to perform a PUT request using pycurl."""
    buffer = io.BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.UPLOAD, 1)
    c.setopt(c.READDATA, io.BytesIO(data))
    c.setopt(c.INFILESIZE, len(data))
    c.setopt(c.WRITEDATA, buffer)
    if headers:
        c.setopt(c.HTTPHEADER, headers)
    c.perform()
    c.close()
    return buffer.getvalue().decode('utf-8')


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
            api_resp = json.loads(pycurl_post(url, payload))
            s3_resp = pycurl_put(api_resp['url'], chunk_data, headers=api_resp['headers'])
            if not s3_resp:
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
    pycurl_post(url, payload)


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

    start_response = json.loads(pycurl_post(config.MULTIPART_START_URL, payload))
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

    # Retry logic for the final POST request
    retries = 7
    backoff_factor = 0.2
    for attempt in range(retries):
        try:
            response = pycurl_post(complete_url, payload, headers=config.HEADERS)
            response_data = json.loads(response)
            if response_data.get('status') == 'success':
                return response_data
        except Exception as e:
            log.error('Retry %d: %s', attempt + 1, str(e))
            time.sleep(backoff_factor * (2 ** attempt))

    raise Exception('Invalid complete response after retries')
