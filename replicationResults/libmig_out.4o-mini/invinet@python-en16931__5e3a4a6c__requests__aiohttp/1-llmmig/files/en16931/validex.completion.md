### Explanation of Changes

To migrate the code from using the `requests` library to the `aiohttp` library, several key changes were made:

1. **Asynchronous Functions**: The `aiohttp` library is designed for asynchronous programming, so the functions that make HTTP requests need to be defined as `async` functions. This allows them to be awaited.

2. **Session Management**: In `aiohttp`, it's common to create a session object that is reused for making requests. This is different from `requests`, where each call creates a new session.

3. **Awaiting Responses**: The `aiohttp` library requires the use of `await` when making requests and when reading the response data.

4. **Error Handling**: The error handling remains similar, but it is wrapped in an asynchronous context.

5. **Payload and Headers**: The way to send JSON data and headers remains largely the same, but the method calls are adjusted to fit the `aiohttp` syntax.

Here is the modified code:

```python
"""
Module to interact with open.validex.net

You need to create an user at validex.net to be able to
use its API.

"""

import base64
import aiohttp
import time
import asyncio

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
    
    async with aiohttp.ClientSession() as session:
        async with session.post(URL, json=payload, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                if result.get('report') and result['report'].get('result') and\
                        result['report']['result'] != 'fatal':
                    # Warnings are not reported
                    return True
                elif result.get('report') and result['report'].get('id'):
                    raise ValueError(await _get_validation_errors(session, result['report']['id'], api_key))
                else:
                    raise RuntimeError(": ".join(result['error'].values()))
            elif response.status == 401:
                raise RuntimeError("Unauthorized: invalid API_KEY")
            else:
                raise RuntimeError(": ".join((await response.json())['error'].values()))


async def _get_validation_errors(session, report_id, api_key):
    headers = {
        'accept': 'json',
        'Authorization': "apikey={}".format(api_key),
    }
    async with session.get(
        "{}/{}".format(URL.replace('validate', 'report'), report_id),
        headers=headers,
    ) as response:
        if response.status == 200:
            resp = await response.json()
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
            raise RuntimeError(": ".join((await response.json())['error'].values()))
```

### Note
- The `asyncio` library is typically used to run the asynchronous functions, so you may need to ensure that the calling context is set up to handle asynchronous execution.