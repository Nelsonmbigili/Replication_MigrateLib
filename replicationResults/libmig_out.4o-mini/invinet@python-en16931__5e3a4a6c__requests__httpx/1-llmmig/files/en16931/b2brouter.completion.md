### Explanation of Changes
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:

1. **Import Statement**: Changed the import from `requests` to `httpx`.
2. **Request Method**: The method for sending a POST request remains the same (`post`), but it is now called from the `httpx` library.
3. **Response Handling**: The way to access the response's JSON content remains similar, but the method to check the status code is now done using `response.status_code` from `httpx`, which behaves the same as in `requests`.

The overall structure and logic of the code remain unchanged, adhering to the requirement of not altering the original coding style or variable names.

### Modified Code
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