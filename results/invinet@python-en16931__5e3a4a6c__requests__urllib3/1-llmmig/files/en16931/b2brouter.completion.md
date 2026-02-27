### Explanation of Changes
To migrate the code from using the `requests` library to `urllib3`, the following changes were made:
1. **Importing `urllib3`**: The `requests` library was replaced with `urllib3`, so the `requests` import was removed, and `urllib3` was imported instead.
2. **HTTP Connection Management**: `urllib3` requires explicit creation of an `HTTPConnectionPool` or `HTTPSConnectionPool` for making requests. A connection pool was created for the base URL (`IMPORT_URL` or `IMPORT_URL_TEST`).
3. **POST Request**: The `requests.post` method was replaced with `urllib3.PoolManager.request` for making POST requests. The `data` parameter was passed as the body of the request, and headers were included.
4. **Response Handling**: The `urllib3` response object differs from `requests`. The response body is accessed using `response.data`, which is in bytes, so it was decoded to a string. JSON parsing was done using `json.loads` instead of `response.json()`.
5. **Error Handling**: The status code and error handling logic were updated to work with `urllib3`.

### Modified Code
```python
"""
Module to interact with b2brouter.net
"""

import urllib3
import json

IMPORT_URL = "https://app.b2brouter.net/projects/{}/invoices/xml.json"
HALTR_URL = "https://app.b2brouter.net"
IMPORT_URL_TEST = "http://localhost:3001/projects/{}/invoices/xml.json"
HALTR_URL_TEST = "http://localhost:3001"


def post_to_b2brouter(invoice, api_key, project_id, test=False):
    """Posts an Invoice to b2brouter.net

    Parameters
    ----------
    api_key: string.
        The authentification API key for b2brouter.net

    project_id: string.
        The project ID to which submit the invoice in b2brouter.net

    """
    payload = invoice.to_xml().encode('utf8')
    import_url = IMPORT_URL.format(project_id) if not test else \
                 IMPORT_URL_TEST.format(project_id)
    headers = {
        'content-type': 'application/octet-stream',
        'X-Redmine-API-Key': api_key,
    }

    # Create a connection pool
    http = urllib3.PoolManager()

    # Make the POST request
    response = http.request(
        "POST",
        import_url,
        body=payload,
        headers=headers
    )

    # Handle the response
    if response.status == 201:  # HTTP 201 Created
        response_data = json.loads(response.data.decode('utf-8'))
        return response_data['invoice']['id']
    elif response.status == 401:  # HTTP 401 Unauthorized
        raise RuntimeError("Unauthorized: invalid API_KEY")
    else:
        response_data = json.loads(response.data.decode('utf-8'))
        raise RuntimeError("\n".join(response_data['errors']))
```

### Key Notes
- The `urllib3.PoolManager` is used to manage HTTP connections.
- The `response.data` from `urllib3` is in bytes, so it is decoded to a string before parsing as JSON.
- The `response.status` attribute is used to check the HTTP status code, replacing `response.status_code` from `requests`.
- The error handling logic remains the same, but it uses `json.loads` to parse the response body.