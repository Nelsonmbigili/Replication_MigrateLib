### Explanation of Changes
To migrate the code from using the `requests` library to the `treq` library, the following changes were made:

1. **Import Statement**: The import statement was changed from `from filestack.utils import requests` to `import treq`.
2. **Request Method**: The `requests.post` method was replaced with `treq.post`. The parameters remain the same, as `treq` supports similar arguments.
3. **Response Handling**: The way to get the JSON response changed from `response.json()` to `response.json()` in `treq`, which is similar to `requests`.

The overall structure and logic of the code remain unchanged, adhering to the requirement of not altering the original coding style or functionality.

### Modified Code
```python
from filestack import config
import treq


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

    response = treq.post('{}/process'.format(config.CDN_URL), json=payload)
    return response.json()
```