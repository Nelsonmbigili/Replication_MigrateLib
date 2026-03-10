### Explanation of Changes
To migrate the code from using the `requests` library to the `treq` library, the following changes were made:

1. **Import Statement**: Changed the import from `requests` to `treq`.
2. **Post Request**: Replaced `requests.post` with `treq.post`. The `treq` library has a similar interface to `requests`, so the method call remains largely the same.
3. **Response Handling**: The response handling remains similar, but the method to get the JSON response is slightly different. In `treq`, we use `response.json()` directly after the post request.

Here is the modified code:

```python
"""
Module to interact with b2brouter.net
"""

import treq

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
    response = treq.post(import_url, data=payload, headers=headers)
    if response.status_code == 201:
        return response.json()['invoice']['id']
    elif response.status_code == 401:
        raise RuntimeError("Unauthorized: invalid API_KEY")
    else:
        raise RuntimeError("\n".join(response.json()['errors']))
```