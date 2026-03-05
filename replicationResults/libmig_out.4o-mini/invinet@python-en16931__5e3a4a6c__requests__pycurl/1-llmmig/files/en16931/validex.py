"""
Module to interact with open.validex.net

You need to create an user at validex.net to be able to
use its API.

"""

import base64
import pycurl
import time
from io import BytesIO

URL = "https://api2.validex.net/api/validate"


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
    headers = [
        'Content-Type: application/json',
        'Accept: application/json',
        'Authorization: apikey={}'.format(api_key),
    ]

    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, URL)
    c.setopt(c.POST, 1)
    c.setopt(c.POSTFIELDS, json.dumps(payload))
    c.setopt(c.HTTPHEADER, headers)
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.setopt(c.SSL_VERIFYPEER, 0)  # equivalent to verify=False

    try:
        c.perform()
        response_code = c.getinfo(c.RESPONSE_CODE)
        response_body = buffer.getvalue().decode('utf-8')
        if response_code == 200:
            result = json.loads(response_body)
            if result.get('report') and result['report'].get('result') and\
                    result['report']['result'] != 'fatal':
                # Warnings are not reported
                return True
            elif result.get('report') and result['report'].get('id'):
                raise ValueError(_get_validation_errors(result['report']['id'], api_key))
            else:
                raise RuntimeError(": ".join(result['error'].values()))
        elif response_code == 401:
            raise RuntimeError("Unauthorized: invalid API_KEY")
        else:
            raise RuntimeError(": ".join(result['error'].values()))
    finally:
        c.close()


def _get_validation_errors(report_id, api_key):
    headers = [
        'Accept: application/json',
        'Authorization: apikey={}'.format(api_key),
    ]

    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, "{}/{}".format(URL.replace('validate', 'report'), report_id))
    c.setopt(c.HTTPHEADER, headers)
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.setopt(c.SSL_VERIFYPEER, 0)  # equivalent to verify=False

    try:
        c.perform()
        response_code = c.getinfo(c.RESPONSE_CODE)
        response_body = buffer.getvalue().decode('utf-8')
        if response_code == 200:
            resp = json.loads(response_body)
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
        elif response_code == 401:
            raise RuntimeError("Unauthorized: invalid API_KEY")
        else:
            raise RuntimeError(": ".join(result['error'].values()))
    finally:
        c.close()
