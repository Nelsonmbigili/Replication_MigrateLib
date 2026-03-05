"""
Module to interact with b2brouter.net
"""

import pycurl
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
    
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, import_url)
    c.setopt(c.POSTFIELDS, payload)
    c.setopt(c.HTTPHEADER, [
        'content-type: application/octet-stream',
        'X-Redmine-API-Key: {}'.format(api_key),
    ])
    c.setopt(c.WRITEDATA, buffer)
    
    try:
        c.perform()
        response_code = c.getinfo(c.RESPONSE_CODE)
        response_body = buffer.getvalue().decode('utf8')
        
        if response_code == 201:
            return json.loads(response_body)['invoice']['id']
        elif response_code == 401:
            raise RuntimeError("Unauthorized: invalid API_KEY")
        else:
            raise RuntimeError("\n".join(json.loads(response_body)['errors']))
    finally:
        c.close()
