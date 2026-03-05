### Explanation of Changes
To migrate the code from using the `requests` library to the `aiohttp` library, several key changes were made:

1. **Importing aiohttp**: The `requests` library was replaced with `aiohttp`, which is designed for asynchronous HTTP requests.
2. **Asynchronous Function**: The `post_to_b2brouter` function was modified to be asynchronous by adding the `async` keyword. This allows the function to use `await` for making HTTP requests.
3. **Session Management**: Instead of directly calling `requests.post`, we create an `aiohttp.ClientSession` to manage the connection and make the POST request.
4. **Awaiting the Response**: The response from the POST request is awaited, and we handle the response asynchronously.
5. **Error Handling**: The error handling remains similar, but we check the status code of the response after awaiting it.

Here is the modified code:

```python
"""
Module to interact with b2brouter.net
"""

import aiohttp
import asyncio

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
    
    async with aiohttp.ClientSession() as session:
        async with session.post(import_url, data=payload, headers=headers) as response:
            if response.status == 201:
                return (await response.json())['invoice']['id']
            elif response.status == 401:
                raise RuntimeError("Unauthorized: invalid API_KEY")
            else:
                raise RuntimeError("\n".join((await response.json())['errors']))
```

### Note
- The function `post_to_b2brouter` is now asynchronous, so it should be called within an asynchronous context (e.g., using `await post_to_b2brouter(...)`).
- Ensure that the rest of your application is set up to handle asynchronous calls properly.