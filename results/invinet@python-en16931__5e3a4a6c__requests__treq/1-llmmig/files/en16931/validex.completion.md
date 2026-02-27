### Explanation of Changes
The migration from `requests` to `treq` involves the following changes:
1. **Asynchronous Nature of `treq`**: `treq` is built on top of `Twisted` and is asynchronous. Therefore, the functions interacting with `treq` need to be converted to `async def` and use `await` for `treq` calls.
2. **API Differences**:
   - `requests.post` and `requests.get` are replaced with `treq.post` and `treq.get`.
   - `treq` does not have a `verify` parameter for SSL verification. Instead, you can pass a `treq`-specific `Agent` with custom SSL options if needed. For simplicity, this example assumes default SSL behavior.
   - `response.json()` in `requests` is replaced with `await response.json()` in `treq`.
   - `response.status_code` in `requests` is replaced with `response.code` in `treq`.
3. **Error Handling**: `treq` does not raise exceptions for HTTP errors (e.g., 4xx or 5xx). You need to manually check the status code and handle errors accordingly.
4. **Base64 Encoding**: No changes are needed for this part since it is independent of the HTTP library.

Below is the modified code.

---

### Modified Code
```python
"""
Module to interact with open.validex.net

You need to create an user at validex.net to be able to
use its API.

"""

import base64
import treq
import time

URL = "https://api2.validex.net/api/validate"


async def is_valid_at_validex(invoice, api_key, user_id):
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
    response = await treq.post(URL, json=payload, headers=headers)
    if response.code == 200:
        result = await response.json()
        if result.get('report') and result['report'].get('result') and\
                result['report']['result'] != 'fatal':
            # Warnings are not reported
            return True
        elif result.get('report') and result['report'].get('id'):
            raise ValueError(await _get_validation_errors(result['report']['id'], api_key))
        else:
            error = await response.json()
            raise RuntimeError(": ".join(error['error'].values()))
    elif response.code == 401:
        raise RuntimeError("Unauthorized: invalid API_KEY")
    else:
        error = await response.json()
        raise RuntimeError(": ".join(error['error'].values()))


async def _get_validation_errors(report_id, api_key):
    headers = {
        'accept': 'json',
        'Authorization': "apikey={}".format(api_key),
    }
    response = await treq.get(
        "{}/{}".format(URL.replace('validate', 'report'), report_id),
        headers=headers,
    )
    if response.code == 200:
        resp = await response.json()
        errors = []
        validation_steps = []
        if resp['report'].get('validationSteps'):
            validation_steps.extend(resp['report']['validationSteps'])
        for step in validation_steps:
            if step.get('success') or not step.get('errors'):
                continue
            for error in step['errors']:
                if error.get('message'):
                    errors.append("{}: {}".format(step['description'], error['message']))
                elif error.get('text'):
                    errors.append("{}: {}".format(step['description'], error['text']))
                else:
                    errors.append(str(error))
        return ". ".join(errors)
    elif response.code == 401:
        raise RuntimeError("Unauthorized: invalid API_KEY")
    else:
        error = await response.json()
        raise RuntimeError(": ".join(error['error'].values()))
```

---

### Key Notes
1. **Asynchronous Functions**: Both `is_valid_at_validex` and `_get_validation_errors` are now `async def` functions. Any code calling these functions must also be asynchronous and use `await`.
2. **Error Handling**: The error handling logic remains the same, but it now uses `await` to retrieve the JSON response from `treq`.
3. **SSL Verification**: The `verify=False` parameter from `requests` is not directly supported in `treq`. If custom SSL behavior is required, you would need to configure a `treq`-specific `Agent`.

This code assumes that the rest of the application is compatible with asynchronous functions. If not, additional changes may be required to integrate the asynchronous code.