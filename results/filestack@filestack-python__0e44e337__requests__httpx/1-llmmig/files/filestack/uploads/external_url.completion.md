### Explanation of Changes
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:
1. **Import Change**: The `requests` module from `filestack.utils` was replaced with `httpx`.
2. **HTTP Method Call**: The `requests.post` method was replaced with `httpx.post`. The syntax for `httpx.post` is similar to `requests.post`, so no additional changes were needed for the arguments.
3. **Response Handling**: The `response.json()` method remains the same, as both `requests` and `httpx` provide this method for parsing JSON responses.

### Modified Code
```python
from filestack import config
from filestack.utils import httpx


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

    response = httpx.post('{}/process'.format(config.CDN_URL), json=payload)
    return response.json()
```