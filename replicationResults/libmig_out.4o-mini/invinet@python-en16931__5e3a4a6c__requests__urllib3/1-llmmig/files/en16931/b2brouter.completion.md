### Explanation of Changes
To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Import Statement**: The import statement was changed from `import requests` to `import urllib3`.
2. **Creating a PoolManager**: `urllib3` requires a `PoolManager` instance to handle connections, so I created an instance of `urllib3.PoolManager()`.
3. **Making the POST Request**: The `requests.post` method was replaced with `http.request('POST', ...)` from `urllib3`, which requires specifying the method and passing the URL, headers, and body data differently.
4. **Handling the Response**: The response handling was adjusted to work with `urllib3`, which does not have a `status_code` attribute but instead uses `response.status`. The JSON response is parsed using `response.data` and `json.loads()`.

Here is the modified code:

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

http = urllib3.PoolManager()

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
    response = http.request('POST', import_url, body=payload, headers=headers)
    if response.status == 201:
        return json.loads(response.data.decode('utf-8'))['invoice']['id']
    elif response.status == 401:
        raise RuntimeError("Unauthorized: invalid API_KEY")
    else:
        raise RuntimeError("\n".join(json.loads(response.data.decode('utf-8'))['errors']))
```