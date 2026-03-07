### Explanation of Changes
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:

1. **Import Statement**: Changed the import from `requests` to `httpx`.
2. **Request Method**: The `requests.post` method was replaced with `httpx.post`. The usage remains similar, but `httpx` is asynchronous by default, so it is important to ensure that the function is called in an appropriate context if you decide to use its async features. However, in this case, we are keeping it synchronous for compatibility with the original code.
3. **Response Handling**: The way to access the JSON response remains the same, so `response.json()` is still valid.

Here is the modified code:

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