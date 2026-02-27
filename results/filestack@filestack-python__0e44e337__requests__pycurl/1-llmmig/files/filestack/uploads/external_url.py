from filestack import config
from filestack.utils import requests  # This import is retained for compatibility with the larger application
import pycurl
import json
from io import BytesIO


def upload_external_url(url, apikey, storage, store_params=None, security=None):
    store_params = store_params or {}
    if storage and not store_params.get('location'):
        store_params['location'] = storage

    # remove params that are currently not supported in external url upload
    for item in ('mimetype', 'upload_tags'):
        store_params.pop(item, None)

    payload = {
        'apikey': apikey,
        'sources': [url],
        'tasks': [{
            'name': 'store',
            'params': store_params
        }]
    }

    if security is not None:
        payload['tasks'].append({
            'name': 'security',
            'params': {
                'policy': security.policy_b64,
                'signature': security.signature
            }
        })

    # Prepare the response buffer
    response_buffer = BytesIO()

    # Initialize pycurl
    curl = pycurl.Curl()
    try:
        # Set the URL
        curl.setopt(pycurl.URL, '{}/process'.format(config.CDN_URL))
        
        # Set HTTP headers
        curl.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])
        
        # Set the POST data
        curl.setopt(pycurl.POST, 1)
        curl.setopt(pycurl.POSTFIELDS, json.dumps(payload))
        
        # Capture the response in the buffer
        curl.setopt(pycurl.WRITEFUNCTION, response_buffer.write)
        
        # Perform the request
        curl.perform()
        
        # Get the HTTP response code (optional, if needed)
        http_code = curl.getinfo(pycurl.RESPONSE_CODE)
        
    finally:
        # Clean up the curl object
        curl.close()

    # Decode and parse the response
    response_data = response_buffer.getvalue().decode('utf-8')
    return json.loads(response_data)
