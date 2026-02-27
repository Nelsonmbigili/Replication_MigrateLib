"""
Module to interact with b2brouter.net
"""

import aiohttp
import asyncio

IMPORT_URL = "https://app.b2brouter.net/projects/{}/invoices/xml.json"
HALTR_URL = "https://app.b2brouter.net"
IMPORT_URL_TEST = "http://localhost:3001/projects/{}/invoices/xml.json"
HALTR_URL_TEST = "http://localhost:3001"


async def post_to_b2brouter(invoice, api_key, project_id, test=False):
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

    async with aiohttp.ClientSession() as session:
        async with session.post(import_url, data=payload, headers=headers) as response:
            if response.status == 201:
                response_data = await response.json()
                return response_data['invoice']['id']
            elif response.status == 401:
                raise RuntimeError("Unauthorized: invalid API_KEY")
            else:
                response_data = await response.json()
                raise RuntimeError("\n".join(response_data['errors']))
