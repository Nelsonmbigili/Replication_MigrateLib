"""
Module to interact with b2brouter.net
"""

import urllib3
import json

IMPORT_URL = "https://app.b2brouter.net/projects/{}/invoices/xml.json"
HALTR_URL = "https://app.b2brouter.net"
IMPORT_URL_TEST = "http://localhost:3001/projects/{}/invoices/xml.json"
HALTR_URL_TEST = "http://localhost:3001"

http = urllib3.PoolManager()

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
    headers = {
        'content-type': 'application/octet-stream',
        'X-Redmine-API-Key': api_key,
    }
    response = http.request('POST', import_url, body=payload, headers=headers)
    if response.status == 201:
        return json.loads(response.data.decode('utf-8'))['invoice']['id']
    elif response.status == 401:
        raise RuntimeError("Unauthorized: invalid API_KEY")
    else:
        raise RuntimeError("\n".join(json.loads(response.data.decode('utf-8'))['errors']))
