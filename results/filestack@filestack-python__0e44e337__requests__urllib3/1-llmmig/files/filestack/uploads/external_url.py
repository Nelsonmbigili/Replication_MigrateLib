from filestack import config
from filestack.utils import requests  # Assuming this is still needed elsewhere in the application
import urllib3
import json


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

    # Create a PoolManager instance for making requests
    http = urllib3.PoolManager()

    # Make the POST request
    response = http.request(
        'POST',
        '{}/process'.format(config.CDN_URL),
        body=json.dumps(payload),  # Convert the payload to a JSON string
        headers={'Content-Type': 'application/json'}  # Set the Content-Type header
    )

    # Parse the JSON response
    return json.loads(response.data.decode('utf-8'))
