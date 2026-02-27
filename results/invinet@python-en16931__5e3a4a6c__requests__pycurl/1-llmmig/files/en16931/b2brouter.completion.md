### Explanation of Changes
To migrate the code from using the `requests` library to `pycurl`, the following changes were made:
1. **Replaced `requests.post` with `pycurl`**:
   - `pycurl` requires setting up a `pycurl.Curl` object and configuring it with the appropriate options (e.g., URL, HTTP headers, POST data).
   - The `pycurl` library does not automatically handle JSON responses, so additional steps were added to parse the response using the `json` module.
2. **Headers**:
   - Headers were set using the `setopt(pycurl.HTTPHEADER, ...)` method.
3. **Payload**:
   - The POST data was set using `setopt(pycurl.POSTFIELDS, ...)`.
4. **Response Handling**:
   - `pycurl` writes the response to a buffer, so a `BytesIO` object was used to capture the response body.
   - The response status code was retrieved using `getinfo(pycurl.RESPONSE_CODE)`.
5. **Error Handling**:
   - `pycurl` raises exceptions for connection issues, so a `try-except` block was added to handle these errors.

Below is the modified code:

---

### Modified Code
```python
"""
Module to interact with b2brouter.net
"""

import pycurl
import json
from io import BytesIO

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
    headers = [
        'Content-Type: application/octet-stream',
        f'X-Redmine-API-Key: {api_key}',
    ]

    # Prepare a buffer to capture the response
    response_buffer = BytesIO()

    # Initialize pycurl
    curl = pycurl.Curl()
    try:
        curl.setopt(pycurl.URL, import_url)
        curl.setopt(pycurl.POST, 1)
        curl.setopt(pycurl.POSTFIELDS, payload)
        curl.setopt(pycurl.HTTPHEADER, headers)
        curl.setopt(pycurl.WRITEFUNCTION, response_buffer.write)

        # Perform the request
        curl.perform()

        # Get the HTTP response code
        status_code = curl.getinfo(pycurl.RESPONSE_CODE)

        # Parse the response
        response_body = response_buffer.getvalue().decode('utf-8')
        response_json = json.loads(response_body)

        if status_code == 201:
            return response_json['invoice']['id']
        elif status_code == 401:
            raise RuntimeError("Unauthorized: invalid API_KEY")
        else:
            raise RuntimeError("\n".join(response_json['errors']))

    except pycurl.error as e:
        raise RuntimeError(f"An error occurred while making the request: {e}")
    finally:
        # Clean up
        curl.close()
        response_buffer.close()
```

---

### Key Notes
1. **Dependencies**:
   - Ensure that the `pycurl` library is installed in your environment (`pip install pycurl`).
2. **Behavior**:
   - The behavior of the function remains the same as the original `requests` implementation.
3. **Error Handling**:
   - `pycurl.error` exceptions are caught and re-raised as `RuntimeError` for consistency with the original code's error handling style.