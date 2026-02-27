### Explanation of Changes
The migration from the `requests` library to the `treq` library involves the following changes:
1. **Asynchronous Nature of `treq`**: `treq` is an asynchronous HTTP client, so the function must be converted to an `async` function to accommodate `await` calls.
2. **Replacing `requests.post`**: The `requests.post` method is replaced with `treq.post`, which is an asynchronous function. The `json` parameter in `requests.post` is replaced with `data` in `treq.post`, and the payload must be serialized using `json.dumps`.
3. **Handling the Response**: The `response.json()` method in `requests` is replaced with `await response.json()` in `treq`. This requires importing `treq` and using its `json_content` helper function to parse the JSON response.
4. **Adjusting Imports**: The `requests` import is removed, and `treq` is imported instead.

### Modified Code
```python
import json
from filestack import config
import treq


async def upload_external_url(url, apikey, storage, store_params=None, security=None):
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

    response = await treq.post(
        '{}/process'.format(config.CDN_URL),
        data=json.dumps(payload),
        headers={'Content-Type': 'application/json'}
    )
    return await response.json()
```

### Key Points
- The function is now asynchronous (`async def`).
- `treq.post` is used with `data=json.dumps(payload)` and a `Content-Type` header.
- The response is parsed using `await response.json()` to handle the asynchronous nature of `treq`.