### Explanation of Changes
To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Import Statement**: The import statement for `requests` was replaced with `urllib3`. 
2. **Creating a Pool Manager**: `urllib3` requires a `PoolManager` to handle connections, so an instance of `PoolManager` was created.
3. **Making the POST Request**: The `requests.post` method was replaced with `http.request('POST', ...)` from `urllib3`, and the payload was converted to JSON format using `json.dumps()`.
4. **Handling the Response**: The response from `urllib3` is different from `requests`, so the response data was accessed using `response.data` and then decoded from bytes to a string before parsing it as JSON.

Here is the modified code:

```python
from filestack import config
import urllib3
import json

http = urllib3.PoolManager()

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

    response = http.request('POST', '{}/process'.format(config.CDN_URL), body=json.dumps(payload), headers={'Content-Type': 'application/json'})
    return json.loads(response.data.decode('utf-8'))
```