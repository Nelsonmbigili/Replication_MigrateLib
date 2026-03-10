### Explanation of Changes
To migrate the code from using the `requests` library to the `aiohttp` library, several key changes were made:

1. **Import Statement**: The import for `requests` was replaced with `aiohttp`.
2. **Asynchronous Function**: The function `upload_external_url` was modified to be asynchronous by adding the `async` keyword.
3. **Session Management**: An `aiohttp.ClientSession` was created to handle the HTTP requests. This is necessary because `aiohttp` requires a session to make requests.
4. **Awaiting the Response**: The `requests.post` method was replaced with `session.post`, and the response was awaited using the `await` keyword.
5. **JSON Handling**: The response's JSON content is now accessed using `await response.json()`.

Here is the modified code:

```python
from filestack import config
from filestack.utils import aiohttp


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

    async with aiohttp.ClientSession() as session:
        async with session.post('{}/process'.format(config.CDN_URL), json=payload) as response:
            return await response.json()
```