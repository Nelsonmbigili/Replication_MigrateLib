from typing import Optional

import treq

AUTHOMIZE_API_URL = 'https://api.authomize.com'


class ClientError(Exception):
    def __init__(self, message):
        self.message = message


class BaseClient:
    def __init__(self, auth_token: str, base_url: str = AUTHOMIZE_API_URL):
        self.auth_token = auth_token
        self.base_url = base_url
        # Removed session management as treq does not require it
        self.headers = {'Authorization': self.authorization_header}

    @property
    def authorization_header(self) -> str:
        raise NotImplementedError()

    @staticmethod
    def _handle_response(response):
        if response.ok:
            return BaseClient._handle_ok_response(response)
        try:
            response_json = response.json()
            detail = response_json.get('detail')
            if 400 <= response.status_code < 500:
                response.reason = response.text
        except Exception:
            detail = None
        if detail:
            raise ClientError(str(detail))
        response.raise_for_status()

    @staticmethod
    def _handle_ok_response(response) -> dict:
        if content_type := response.headers.get('content-type'):
            if content_type.startswith('application/json'):
                return response.json()

        raise ClientError(
            message={
                'status_code': response.status_code,
                'url': response.url,
                'message': 'Unexpected response from API',
                'raw': response.content,
            },
        )

    def http_get(self, url, params=None):
        url = self.base_url + url
        response = treq.get(url, params=params, headers=self.headers)
        return self._handle_response(response)

    def http_post(self, url: str, body: Optional[str] = None):
        url = self.base_url + url
        response = treq.post(
            url,
            headers={'Content-Type': 'application/json', **self.headers},
            json=body,
        )
        return self._handle_response(response)

    def http_patch(self, url: str, body: Optional[str] = None):
        url = self.base_url + url
        response = treq.patch(
            url,
            headers={'Content-Type': 'application/json', **self.headers},
            json=body,
        )
        return self._handle_response(response)

    def http_delete(self, url: str, params=None):
        url = self.base_url + url
        response = treq.delete(url, params=params, headers=self.headers)
        return self._handle_response(response)
