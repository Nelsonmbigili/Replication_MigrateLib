from filestack import config
from filestack.utils import requests_futures
from requests_futures.sessions import FuturesSession


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

    # Use FuturesSession for asynchronous requests
    session = FuturesSession()
    future_response = session.post('{}/process'.format(config.CDN_URL), json=payload)
    response = future_response.result()  # Wait for the response synchronously
    return response.json()
