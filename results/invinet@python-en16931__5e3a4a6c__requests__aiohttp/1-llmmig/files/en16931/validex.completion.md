### Explanation of Changes
To migrate the code from `requests` to `aiohttp`, the following changes were made:
1. **Asynchronous Programming**: Since `aiohttp` is an asynchronous library, the functions interacting with the API were converted to `async` functions.
2. **Session Management**: `aiohttp` requires an `aiohttp.ClientSession` to make HTTP requests. This was added to the code.
3. **Request Methods**: The `requests.post` and `requests.get` methods were replaced with their `aiohttp` equivalents (`session.post` and `session.get`).
4. **Response Handling**: The `aiohttp` response object requires explicit calls to `await response.json()` or `await response.text()` to retrieve the response body.
5. **Error Handling**: Adjusted error handling to work with `aiohttp` exceptions.
6. **SSL Verification**: The `verify=False` parameter in `requests` was replaced with `ssl=False` in `aiohttp`.

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
import aiohttp
import asyncio
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
        'fileContents64': base64.b64encode(invoice.to_xml().encode('utf8')).decode('utf8'),
    }
    headers = {
        'content_type': 'json',
        'accept': 'json',
        'Authorization': "apikey={}".format(api_key),
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(URL, json=payload, headers=headers, ssl=False) as response:
            if response.status == 200:
                result = await response.json()
                if result.get('report') and result['report'].get('result') and \
                        result['report']['result'] != 'fatal':
                    # Warnings are not reported
                    return True
                elif result.get('report') and result['report'].get('id'):
                    raise ValueError(await _get_validation_errors(result['report']['id'], api_key))
                else:
                    error = await response.json()
                    raise RuntimeError(": ".join(error['error'].values()))
            elif response.status == 401:
                raise RuntimeError("Unauthorized: invalid API_KEY")
            else:
                error = await response.json()
                raise RuntimeError(": ".join(error['error'].values()))


async def _get_validation_errors(report_id, api_key):
    headers = {
        'accept': 'json',
        'Authorization': "apikey={}".format(api_key),
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "{}/{}".format(URL.replace('validate', 'report'), report_id),
            headers=headers,
            ssl=False,
        ) as response:
            if response.status == 200:
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
            elif response.status == 401:
                raise RuntimeError("Unauthorized: invalid API_KEY")
            else:
                error = await response.json()
                raise RuntimeError(": ".join(error['error'].values()))
```

---

### Key Notes
1. **Asynchronous Usage**: The functions `is_valid_at_validex` and `_get_validation_errors` are now `async` functions. They must be called using `await` or within an `async` context.
2. **Base64 Encoding**: The `base64.b64encode` result was decoded to a string (`.decode('utf8')`) because `aiohttp` requires JSON payloads to be serializable.
3. **SSL Verification**: The `ssl=False` parameter disables SSL verification, equivalent to `verify=False` in `requests`.
4. **Error Handling**: The `response.json()` calls are now `await response.json()` to handle the asynchronous nature of `aiohttp`.

This code is now fully migrated to use `aiohttp` while maintaining the original functionality and structure.