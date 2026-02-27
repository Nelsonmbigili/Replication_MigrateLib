### Explanation of Changes
To migrate the code from using the `requests` library to `aiohttp`, the following changes were made:
1. **Asynchronous Programming**: `aiohttp` is an asynchronous library, so the function `upload_external_url` was converted to an `async` function.
2. **Session Management**: `aiohttp` requires an `aiohttp.ClientSession` to make HTTP requests. A session is created using `aiohttp.ClientSession()` and used to perform the `POST` request.
3. **Awaiting Requests**: Since `aiohttp` is asynchronous, the `post` method is awaited using the `await` keyword.
4. **Response Handling**: The `aiohttp` response object provides an `await response.json()` method to parse JSON data asynchronously.
5. **URL Formatting**: The URL construction remains the same, but it is passed to `aiohttp`'s `post` method.

Below is the modified code:

---

### Modified Code
```python
from filestack import config
from filestack.utils import requests
import aiohttp


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
        async with session.post(f'{config.CDN_URL}/process', json=payload) as response:
            return await response.json()
```

---

### Key Points
- The function `upload_external_url` is now an `async` function, so it must be called using `await` in an asynchronous context.
- The `aiohttp.ClientSession` is used to manage the HTTP session, and the `post` method is awaited.
- The `response.json()` method is also awaited to parse the JSON response.

These changes ensure the code is fully migrated to use `aiohttp` while maintaining the original functionality.