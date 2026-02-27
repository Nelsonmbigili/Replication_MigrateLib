"""
Module to interact with open.validex.net

You need to create an user at validex.net to be able to
use its API.

"""

import base64
import pycurl
import time
import json
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
        'fileContents64': base64.b64encode(invoice.to_xml().encode('utf8')).decode('utf8'),
    }
    headers = [
        'Content-Type: application/json',
        'Accept: application/json',
        'Authorization: apikey={}'.format(api_key),
    ]

    response_buffer = BytesIO()
    curl = pycurl.Curl()
    try:
        curl.setopt(pycurl.URL, URL)
        curl.setopt(pycurl.POST, 1)
        curl.setopt(pycurl.POSTFIELDS, json.dumps(payload))
        curl.setopt(pycurl.HTTPHEADER, headers)
        curl.setopt(pycurl.WRITEFUNCTION, response_buffer.write)
        curl.setopt(pycurl.SSL_VERIFYPEER, 0)  # Disable SSL verification
        curl.setopt(pycurl.SSL_VERIFYHOST, 0)  # Disable SSL verification
        curl.perform()

        status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        response_data = response_buffer.getvalue().decode('utf8')

        if status_code == 200:
            result = json.loads(response_data)
            if result.get('report') and result['report'].get('result') and\
                    result['report']['result'] != 'fatal':
                # Warnings are not reported
                return True
            elif result.get('report') and result['report'].get('id'):
                raise ValueError(_get_validation_errors(result['report']['id'], api_key))
            else:
                raise RuntimeError(": ".join(result['error'].values()))
        elif status_code == 401:
            raise RuntimeError("Unauthorized: invalid API_KEY")
        else:
            error_data = json.loads(response_data)
            raise RuntimeError(": ".join(error_data['error'].values()))
    finally:
        curl.close()


def _get_validation_errors(report_id, api_key):
    headers = [
        'Accept: application/json',
        'Authorization: apikey={}'.format(api_key),
    ]

    response_buffer = BytesIO()
    curl = pycurl.Curl()
    try:
        curl.setopt(pycurl.URL, "{}/{}".format(URL.replace('validate', 'report'), report_id))
        curl.setopt(pycurl.HTTPGET, 1)
        curl.setopt(pycurl.HTTPHEADER, headers)
        curl.setopt(pycurl.WRITEFUNCTION, response_buffer.write)
        curl.setopt(pycurl.SSL_VERIFYPEER, 0)  # Disable SSL verification
        curl.setopt(pycurl.SSL_VERIFYHOST, 0)  # Disable SSL verification
        curl.perform()

        status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        response_data = response_buffer.getvalue().decode('utf8')

        if status_code == 200:
            resp = json.loads(response_data)
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
        elif status_code == 401:
            raise RuntimeError("Unauthorized: invalid API_KEY")
        else:
            error_data = json.loads(response_data)
            raise RuntimeError(": ".join(error_data['error'].values()))
    finally:
        curl.close()
