from typing import Optional
import json
import urllib3

AUTHOMIZE_API_URL = 'https://api.authomize.com'


class ClientError(Exception):
    def __init__(self, message):
        self.message = message


class BaseClient:
    def __init__(self, auth_token: str, base_url: str = AUTHOMIZE_API_URL):
        self.auth_token = auth_token
        self.base_url = base_url
        self.session = urllib3.PoolManager()
        self.headers = {'Authorization': self.authorization_header}

    @property
    def authorization_header(self) -> str:
        raise NotImplementedError()

    @staticmethod
    def _handle_response(response: urllib3.HTTPResponse):
        if 200 <= response.status < 300:  # Equivalent to response.ok in requests
            return BaseClient._handle_ok_response(response)
        try:
            response_data = response.data.decode('utf-8')
            response_json = json.loads(response_data)
            detail = response_json.get('detail')
        except Exception:
            detail = None
        if detail:
            raise ClientError(str(detail))
        raise ClientError(f"HTTP Error {response.status}: {response.data.decode('utf-8')}")

    @staticmethod
    def _handle_ok_response(response: urllib3.HTTPResponse) -> dict:
        content_type = response.headers.get('Content-Type')
        if content_type and content_type.startswith('application/json'):
            return json.loads(response.data.decode('utf-8'))

        raise ClientError(
            message={
                'status_code': response.status,
                'url': response.geturl(),
                'message': 'Unexpected response from API',
                'raw': response.data,
            },
        )

    def http_get(self, url, params=None):
        url = self.base_url + url
        response = self.session.request(
            'GET',
            url,
            fields=params,
            headers=self.headers,
        )
        return self._handle_response(response)

    def http_post(self, url: str, body: Optional[str] = None):
        url = self.base_url + url
        response = self.session.request(
            'POST',
            url,
            headers={**self.headers, 'Content-Type': 'application/json'},
            body=body,
        )
        return self._handle_response(response)

    def http_patch(self, url: str, body: Optional[str] = None):
        url = self.base_url + url
        response = self.session.request(
            'PATCH',
            url,
            headers={**self.headers, 'Content-Type': 'application/json'},
            body=body,
        )
        return self._handle_response(response)

    def http_delete(self, url: str, params=None):
        url = self.base_url + url
        response = self.session.request(
            'DELETE',
            url,
            fields=params,
            headers=self.headers,
        )
        return self._handle_response(response)
