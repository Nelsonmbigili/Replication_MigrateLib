from typing import Optional
import pycurl
from io import BytesIO

AUTHOMIZE_API_URL = 'https://api.authomize.com'


class ClientError(Exception):
    def __init__(self, message):
        self.message = message


class BaseClient:
    def __init__(self, auth_token: str, base_url: str = AUTHOMIZE_API_URL):
        self.auth_token = auth_token
        self.base_url = base_url

    @property
    def authorization_header(self) -> str:
        raise NotImplementedError()

    @staticmethod
    def _handle_response(response_body: bytes, response_code: int, response_headers: dict):
        if response_code >= 200 and response_code < 300:
            return BaseClient._handle_ok_response(response_body, response_headers)
        try:
            response_json = json.loads(response_body)
            detail = response_json.get('detail')
            if 400 <= response_code < 500:
                raise ClientError(str(response_body.decode()))
        except Exception:
            detail = None
        if detail:
            raise ClientError(str(detail))
        raise ClientError(f"HTTP Error: {response_code}")

    @staticmethod
    def _handle_ok_response(response_body: bytes, response_headers: dict) -> dict:
        if 'content-type' in response_headers:
            if response_headers['content-type'].startswith('application/json'):
                return json.loads(response_body)

        raise ClientError(
            message={
                'status_code': response_headers.get('status_code', 500),
                'url': response_headers.get('url', ''),
                'message': 'Unexpected response from API',
                'raw': response_body,
            },
        )

    def http_get(self, url, params=None):
        url = self.base_url + url
        if params:
            url += '?' + '&'.join(f"{key}={value}" for key, value in params.items())
        
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.HTTPHEADER, [f'Authorization: {self.authorization_header}'])
        c.perform()
        response_code = c.getinfo(c.RESPONSE_CODE)
        response_headers = c.getinfo(c.HEADER_SIZE)
        c.close()
        
        response_body = buffer.getvalue()
        return self._handle_response(response_body, response_code, response_headers)

    def http_post(self, url: str, body: Optional[str] = None):
        url = self.base_url + url
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.POST, 1)
        c.setopt(c.POSTFIELDS, body)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.HTTPHEADER, ['Content-Type: application/json', f'Authorization: {self.authorization_header}'])
        c.perform()
        response_code = c.getinfo(c.RESPONSE_CODE)
        response_headers = c.getinfo(c.HEADER_SIZE)
        c.close()
        
        response_body = buffer.getvalue()
        return self._handle_response(response_body, response_code, response_headers)

    def http_patch(self, url: str, body: Optional[str] = None):
        url = self.base_url + url
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.CUSTOMREQUEST, 'PATCH')
        c.setopt(c.POSTFIELDS, body)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.HTTPHEADER, ['Content-Type: application/json', f'Authorization: {self.authorization_header}'])
        c.perform()
        response_code = c.getinfo(c.RESPONSE_CODE)
        response_headers = c.getinfo(c.HEADER_SIZE)
        c.close()
        
        response_body = buffer.getvalue()
        return self._handle_response(response_body, response_code, response_headers)

    def http_delete(self, url: str, params=None):
        url = self.base_url + url
        if params:
            url += '?' + '&'.join(f"{key}={value}" for key, value in params.items())
        
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.CUSTOMREQUEST, 'DELETE')
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.HTTPHEADER, [f'Authorization: {self.authorization_header}'])
        c.perform()
        response_code = c.getinfo(c.RESPONSE_CODE)
        response_headers = c.getinfo(c.HEADER_SIZE)
        c.close()
        
        response_body = buffer.getvalue()
        return self._handle_response(response_body, response_code, response_headers)
