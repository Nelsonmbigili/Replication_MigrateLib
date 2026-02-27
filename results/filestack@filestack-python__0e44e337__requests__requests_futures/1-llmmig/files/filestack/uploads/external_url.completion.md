### Explanation of Changes:
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: The `requests` module from `requests_futures` was imported instead of the original `requests` library.
2. **Asynchronous Request Handling**: The `requests_futures` library provides asynchronous capabilities. The `requests.post` method was replaced with `requests.Session().post` to enable asynchronous behavior. The `FuturesSession` class from `requests_futures` was used to create a session.
3. **Response Handling**: Since `requests_futures` returns a `Future` object, the `.result()` method was called on the response to retrieve the actual response object synchronously (to maintain the original behavior of the code).

### Modified Code:
```python
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
```

### Key Notes:
- The `FuturesSession` class is used to enable asynchronous requests, but the `.result()` method ensures the behavior remains synchronous as in the original code.
- No other parts of the code were altered to ensure compatibility with the rest of the application.