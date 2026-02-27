### Explanation of Changes
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `requests_futures.sessions` to use the `FuturesSession` class.
2. **Session Initialization**: Created an instance of `FuturesSession` to handle asynchronous requests.
3. **Asynchronous POST Request**: Replaced the `requests.post` call with `session.post` to make the request asynchronously.
4. **Response Handling**: Since `requests_futures` returns a `Future` object, the `.result()` method is used to retrieve the actual response object before processing it.

These changes ensure that the code now uses `requests_futures` for asynchronous HTTP requests while maintaining the original functionality.

---

### Modified Code
```python
"""
Module to interact with b2brouter.net
"""

from requests_futures.sessions import FuturesSession

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
    session = FuturesSession()  # Initialize a FuturesSession for asynchronous requests
    payload = invoice.to_xml().encode('utf8')
    import_url = IMPORT_URL.format(project_id) if not test else \
                 IMPORT_URL_TEST.format(project_id)
    headers = {
        'content-type': 'application/octet-stream',
        'X-Redmine-API-Key': api_key,
    }
    future = session.post(import_url, data=payload, headers=headers)  # Asynchronous POST request
    response = future.result()  # Wait for the response and retrieve it

    if response.status_code == 201:
        return response.json()['invoice']['id']
    elif response.status_code == 401:
        raise RuntimeError("Unauthorized: invalid API_KEY")
    else:
        raise RuntimeError("\n".join(response.json()['errors']))
```