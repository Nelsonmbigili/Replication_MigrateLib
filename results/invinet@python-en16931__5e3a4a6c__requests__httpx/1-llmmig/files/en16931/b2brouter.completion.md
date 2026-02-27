### Explanation of Changes
To migrate the code from the `requests` library to the `httpx` library, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `httpx`.
2. **POST Request**: Replaced `requests.post` with `httpx.post`. The syntax for `httpx.post` is similar to `requests.post`, so the transition is straightforward.
3. **Response Handling**: The `httpx` response object is similar to the `requests` response object, so no major changes were needed. The `.json()` and `.status_code` methods work the same way.
4. **Error Handling**: The error handling logic remains unchanged since `httpx` raises exceptions in a similar manner to `requests`.

### Modified Code
Here is the complete code after migrating to `httpx`:

```python
"""
Module to interact with b2brouter.net
"""

import httpx

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
    response = httpx.post(import_url, data=payload, headers=headers)
    if response.status_code == 201:
        return response.json()['invoice']['id']
    elif response.status_code == 401:
        raise RuntimeError("Unauthorized: invalid API_KEY")
    else:
        raise RuntimeError("\n".join(response.json()['errors']))
```

### Summary of Changes
- Replaced `import requests` with `import httpx`.
- Replaced `requests.post` with `httpx.post`.
- No other changes were made to the logic, structure, or style of the code.