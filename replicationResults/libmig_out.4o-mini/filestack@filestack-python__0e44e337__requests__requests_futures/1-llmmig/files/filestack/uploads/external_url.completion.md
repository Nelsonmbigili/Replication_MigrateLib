### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the primary change involves replacing the synchronous `requests.post` call with the asynchronous `FuturesSession` from `requests_futures`. This allows the code to handle requests in a non-blocking manner. The `FuturesSession` provides a way to send requests and immediately return a `Future` object, which can be used to retrieve the response later.

### Modified Code
```python
from filestack import config
from filestack.utils import requests
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

    session = FuturesSession()
    future = session.post('{}/process'.format(config.CDN_URL), json=payload)
    response = future.result()  # Wait for the response
    return response.json()
```