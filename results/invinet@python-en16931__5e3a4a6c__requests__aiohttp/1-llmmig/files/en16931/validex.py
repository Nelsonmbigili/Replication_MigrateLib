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
