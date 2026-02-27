### Explanation of Changes
To migrate the code from using the `requests` library to the `treq` library, the following changes were made:
1. **Import Statement**: Replaced the `requests` import with `treq`.
2. **Asynchronous Nature of `treq`**: Since `treq` is asynchronous, the function `post_to_b2brouter` was modified to be an `async` function.
3. **POST Request**: Replaced `requests.post` with `treq.post`. The `treq.post` method is used to send the POST request, and it returns a `Deferred` object, which needs to be awaited.
4. **Response Handling**: 
   - Used `await response.json()` to parse the JSON response.
   - Used `response.code` instead of `response.status_code` to check the HTTP status code.
5. **Error Handling**: Adjusted the error handling to work with the asynchronous nature of `treq`.

### Modified Code
```python
"""
Module to interact with b2brouter.net
"""

import treq

IMPORT_URL = "https://app.b2brouter.net/projects/{}/invoices/xml.json"
HALTR_URL = "https://app.b2brouter.net"
IMPORT_URL_TEST = "http://localhost:3001/projects/{}/invoices/xml.json"
HALTR_URL_TEST = "http://localhost:3001"


async def post_to_b2brouter(invoice, api_key, project_id, test=False):
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
    response = await treq.post(import_url, data=payload, headers=headers)
    if response.code == 201:
        response_json = await response.json()
        return response_json['invoice']['id']
    elif response.code == 401:
        raise RuntimeError("Unauthorized: invalid API_KEY")
    else:
        response_json = await response.json()
        raise RuntimeError("\n".join(response_json['errors']))
```

### Key Notes
- The function `post_to_b2brouter` is now asynchronous (`async def`), so it must be called using `await` or within an asynchronous context.
- The `treq` library is designed for asynchronous programming, so the rest of the application may need to ensure it supports asynchronous calls if it doesn't already.