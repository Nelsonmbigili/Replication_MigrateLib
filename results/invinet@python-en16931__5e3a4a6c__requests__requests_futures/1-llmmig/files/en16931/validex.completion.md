### Explanation of Changes
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `requests_futures.sessions` to use the `FuturesSession` class, which supports asynchronous requests.
2. **Session Initialization**: Created an instance of `FuturesSession` to handle requests instead of directly using `requests`.
3. **Asynchronous Requests**: Updated the `requests.post` and `requests.get` calls to use the `FuturesSession` instance. Since `requests_futures` returns a `Future` object, the `.result()` method is called to block and retrieve the response synchronously (to maintain the original synchronous behavior).
4. **No Other Changes**: The rest of the code remains unchanged to ensure compatibility with the existing application.

### Modified Code
```python
"""
Module to interact with open.validex.net

You need to create an user at validex.net to be able to
use its API.

"""

import base64
from requests_futures.sessions import FuturesSession
import time

URL = "https://api2.validex.net/api/validate"

# Initialize a FuturesSession for asynchronous requests
session = FuturesSession()


def is_valid_at_validex(invoice, api_key, user_id):
    """Validates an Invoice at open.validex.net

    You need to create an user at validex.net to be able to
    use its API.

    Parameters
    ----------
    api_key: string.
        The authentification API key for validex.net

    user_id: string.
        The user ID of validex.net

    Notes
    -----
    Warnings are not reported.

    """
    payload = {
        'userId': user_id,
        'filename': "{}.xml".format(int(time.time())),
        'fileContents64': base64.b64encode(invoice.to_xml().encode('utf8')),
    }
    headers = {
        'content_type': 'json',
        'accept': 'json',
        'Authorization': "apikey={}".format(api_key),
    }
    # Use session.post instead of requests.post
    future = session.post(URL, json=payload, headers=headers, verify=False)
    response = future.result()  # Block and get the response
    if response.status_code == 200:
        result = response.json()
        if result.get('report') and result['report'].get('result') and\
                result['report']['result'] != 'fatal':
            # Warnings are not reported
            return True
        elif result.get('report') and result['report'].get('id'):
            raise ValueError(_get_validation_errors(result['report']['id']))
        else:
            raise RuntimeError(": ".join(response.json()['error'].values()))
    elif response.status_code == 401:
        raise RuntimeError("Unauthorized: invalid API_KEY")
    else:
        raise RuntimeError(": ".join(response.json()['error'].values()))


def _get_validation_errors(report_id):
    headers = {
        'accept': 'json',
        'Authorization': "apikey={}".format(api_key),
    }
    # Use session.get instead of requests.get
    future = session.get(
        "{}/{}".format(URL.replace('validate', 'report'), report_id),
        headers=headers,
        verify=False,
    )
    response = future.result()  # Block and get the response
    if response.status_code == 200:
        resp = response.json()
        errors = []
        validation_steps = []
        if resp['report'].get('validationSteps'):
            validation_steps.extend(resp['report']['validationSteps'])
        for step in validation_steps:
            if step.get('success') or not step.get('errors'):
                continue
            for error in step['errors']:
                if error.get('message'):
                    errors.add("{}: {}".format(step['description'], error['message']))
                elif error.get('text'):
                    errors.add("{}: {}".format(step['description'], error['text']))
                else:
                    errors.add(str(error))
        return ". ".join(errors)
    elif response.status_code == 401:
        raise RuntimeError("Unauthorized: invalid API_KEY")
    else:
        raise RuntimeError(": ".join(response.json()['error'].values()))
```

### Key Notes
- The `FuturesSession` class from `requests_futures` is used to make asynchronous HTTP requests.
- The `.result()` method is called on the `Future` object returned by `session.post` and `session.get` to block and retrieve the response, preserving the original synchronous behavior of the code.
- No other parts of the code were modified to ensure compatibility with the existing application.