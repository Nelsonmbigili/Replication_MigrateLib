from filestack import config
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

    # Prepare the payload as a JSON string
    json_payload = json.dumps(payload)

    # Create a buffer to capture the response
    response_buffer = BytesIO()

    # Initialize a pycurl object
    c = pycurl.Curl()
    c.setopt(c.URL, '{}/process'.format(config.CDN_URL))
    c.setopt(c.POST, 1)
    c.setopt(c.POSTFIELDS, json_payload)
    c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])
    c.setopt(c.WRITEDATA, response_buffer)

    # Perform the request
    c.perform()

    # Clean up
    c.close()

    # Get the response data
    response_data = response_buffer.getvalue().decode('utf-8')
    return json.loads(response_data)
