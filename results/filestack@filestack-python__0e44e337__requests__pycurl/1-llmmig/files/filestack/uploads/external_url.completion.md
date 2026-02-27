### Explanation of Changes:
To migrate the code from using the `requests` library to `pycurl`, the following changes were made:
1. **Replaced `requests.post`**: The `requests.post` method was replaced with `pycurl` to perform the HTTP POST request.
2. **Set up `pycurl` options**: `pycurl` requires explicit configuration of options such as the URL, HTTP headers, and payload. These were added using the `setopt` method.
3. **Encoded the JSON payload**: Since `pycurl` does not handle JSON encoding automatically, the `json.dumps` function was used to convert the payload to a JSON string.
4. **Captured the response**: `pycurl` writes the response to a buffer, so a `BytesIO` object was used to capture the response body.
5. **Parsed the response**: The response captured in the buffer was decoded and parsed as JSON.

### Modified Code:
```python
from filestack import config
from filestack.utils import requests  # This import is retained for compatibility with the larger application
import pycurl
import json
from io import BytesIO


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

    # Prepare the response buffer
    response_buffer = BytesIO()

    # Initialize pycurl
    curl = pycurl.Curl()
    try:
        # Set the URL
        curl.setopt(pycurl.URL, '{}/process'.format(config.CDN_URL))
        
        # Set HTTP headers
        curl.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])
        
        # Set the POST data
        curl.setopt(pycurl.POST, 1)
        curl.setopt(pycurl.POSTFIELDS, json.dumps(payload))
        
        # Capture the response in the buffer
        curl.setopt(pycurl.WRITEFUNCTION, response_buffer.write)
        
        # Perform the request
        curl.perform()
        
        # Get the HTTP response code (optional, if needed)
        http_code = curl.getinfo(pycurl.RESPONSE_CODE)
        
    finally:
        # Clean up the curl object
        curl.close()

    # Decode and parse the response
    response_data = response_buffer.getvalue().decode('utf-8')
    return json.loads(response_data)
```

### Key Notes:
- The `pycurl` library requires more manual setup compared to `requests`, such as explicitly setting headers, encoding the payload, and capturing the response.
- The `requests` import was retained in the code to avoid breaking the larger application, even though it is no longer used in this function.
- The `pycurl` configuration ensures that the behavior of the migrated code matches the original functionality.