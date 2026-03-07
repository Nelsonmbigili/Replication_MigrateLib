### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Import Statement**: The import statement was changed from `import requests` to `from requests_futures.sessions import FuturesSession`. This is necessary because `requests_futures` provides a `FuturesSession` class that allows for asynchronous requests.
  
2. **Session Creation**: Instead of directly using `requests.post`, a `FuturesSession` object was created to handle the request. This allows the request to be sent asynchronously.

3. **Handling the Response**: The response from the asynchronous request is accessed using the `result()` method of the `Future` object returned by the `FuturesSession`. This is necessary to retrieve the actual response after the request is completed.

Here is the modified code:

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
    payload = invoice.to_xml().encode('utf8')
    import_url = IMPORT_URL.format(project_id) if not test else \
                 IMPORT_URL_TEST.format(project_id)
    headers = {
        'content-type': 'application/octet-stream',
        'X-Redmine-API-Key': api_key,
    }
    
    session = FuturesSession()
    future = session.post(import_url, data=payload, headers=headers)
    response = future.result()  # Wait for the request to complete
    
    if response.status_code == 201:
        return response.json()['invoice']['id']
    elif response.status_code == 401:
        raise RuntimeError("Unauthorized: invalid API_KEY")
    else:
        raise RuntimeError("\n".join(response.json()['errors']))
``` 

This code now uses `requests_futures` to handle the HTTP POST request asynchronously while maintaining the original functionality and structure.