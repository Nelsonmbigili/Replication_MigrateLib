### Explanation of Changes

To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Import Statement**: The import statement for `requests` was replaced with `urllib3`.
2. **Creating a Pool Manager**: A `PoolManager` instance was created to handle connections.
3. **Making Requests**: The `requests.post` and `requests.get` methods were replaced with `http.request('POST', ...)` and `http.request('GET', ...)` respectively.
4. **Handling JSON**: The `json` parameter in `requests` was replaced with manually encoding the payload to JSON using `json.dumps()` and setting the appropriate headers.
5. **Response Handling**: The response from `urllib3` does not have a `json()` method, so the response data was parsed using `json.loads()` after reading the response data.
6. **Error Handling**: The status code checking was adapted to work with the `urllib3` response object.

Here is the modified code:

```python
"""
Module to interact with open.validex.net

You need to create an user at validex.net to be able to
use its API.

"""

import base64
import urllib3
import json
import time

URL = "https://api2.validex.net/api/validate"
http = urllib3.PoolManager()

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
        'fileContents64': base64.b64encode(invoice.to_xml().encode('utf8')).decode('utf-8'),
    }
    headers = {
        'content-type': 'application/json',
        'accept': 'application/json',
        'Authorization': "apikey={}".format(api_key),
    }
    response = http.request('POST', URL, body=json.dumps(payload), headers=headers)
    if response.status == 200:
        result = json.loads(response.data.decode('utf-8'))
        if result.get('report') and result['report'].get('result') and\
                result['report']['result'] != 'fatal':
            # Warnings are not reported
            return True
        elif result.get('report') and result['report'].get('id'):
            raise ValueError(_get_validation_errors(result['report']['id']))
        else:
            raise RuntimeError(": ".join(result['error'].values()))
    elif response.status == 401:
        raise RuntimeError("Unauthorized: invalid API_KEY")
    else:
        raise RuntimeError(": ".join(json.loads(response.data.decode('utf-8'))['error'].values()))


def _get_validation_errors(report_id):
    headers = {
        'accept': 'application/json',
        'Authorization': "apikey={}".format(api_key),
    }
    response = http.request(
        'GET',
        "{}/{}".format(URL.replace('validate', 'report'), report_id),
        headers=headers,
    )
    if response.status == 200:
        resp = json.loads(response.data.decode('utf-8'))
        errors = set()
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
    elif response.status == 401:
        raise RuntimeError("Unauthorized: invalid API_KEY")
    else:
        raise RuntimeError(": ".join(json.loads(response.data.decode('utf-8'))['error'].values()))
```