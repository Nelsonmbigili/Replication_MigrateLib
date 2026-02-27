import os
import hashlib
import mimetypes
import multiprocessing
from base64 import b64encode
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

import pycurl

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


def pycurl_post(url, json_payload):
    """Helper function to perform a POST request using pycurl."""
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.POST, 1)
    c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])
    c.setopt(c.POSTFIELDS, json_payload)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    return buffer.getvalue().decode('utf-8')


def pycurl_put(url, headers, data):
    """Helper function to perform a PUT request using pycurl."""
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.UPLOAD, 1)
    c.setopt(c.HTTPHEADER, [f'{key}: {value}' for key, value in headers.items()])
    c.setopt(c.READDATA, BytesIO(data))
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    response_headers = c.getinfo(pycurl.RESPONSE_CODE)
    c.close()
    return buffer.getvalue().decode('utf-8'), response_headers


def multipart_request(url, payload, params=None, security=None):
    for key in ('path', 'location', 'region', 'container', 'access'):
        if key in params:
            payload['store'][key] = params[key]

    if security:
        payload.update({
            'policy': security.policy_b64,
            'signature': security.signature
        })

    response = pycurl_post(url, json.dumps(payload))
    return json.loads(response)


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

    fs_resp = json.loads(pycurl_post(
        'https://{}/multipart/upload'.format(start_response['location_url']),
        json.dumps(payload)
    ))

    resp_data, resp_headers = pycurl_put(fs_resp['url'], fs_resp['headers'], chunk.bytes)

    return {'part_number': chunk.num, 'etag': resp_headers.get('ETag')}


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
