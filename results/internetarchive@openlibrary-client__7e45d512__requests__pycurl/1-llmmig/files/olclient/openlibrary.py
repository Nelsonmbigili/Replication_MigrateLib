import pycurl
from io import BytesIO
import json
from urllib.parse import urlencode
import logging
import os
import re
import backoff
from typing import List, Dict, Optional, Any

import jsonschema
from urllib.request import pathname2url

from olclient import common
from olclient.config import Config
from olclient.entity_helpers.work import get_work_helper_class
from olclient.utils import merge_unique_lists

logger = logging.getLogger('openlibrary')


class PyCurlResponse:
    """Custom response object to mimic `requests.Response`."""
    def __init__(self, body: bytes, status_code: int, headers: Dict[str, str]):
        self.body = body
        self.status_code = status_code
        self.headers = headers

    def json(self):
        return json.loads(self.body.decode('utf-8'))

    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise Exception(f"HTTP Error: {self.status_code}, Response: {self.body}")


class OpenLibrary:
    """Open Library API Client using pycurl."""

    VALID_IDS = ['isbn_10', 'isbn_13', 'lccn', 'ocaid']
    BACKOFF_KWARGS = {
        'wait_gen': backoff.expo,
        'exception': pycurl.error,
        'giveup': lambda e: isinstance(e, pycurl.error),
        'max_tries': 5,
    }

    WORKS_LIMIT = 50
    WORKS_PAGINATION_OFFSET = 0

    def __init__(self, credentials=None, base_url='https://openlibrary.org'):
        self.base_url = base_url
        self.credentials = credentials or Config().get_config().get('s3', None)
        self.curl_share = pycurl.CurlShare()
        self.curl_share.setopt(pycurl.SH_SHARE, pycurl.LOCK_DATA_COOKIE)
        self.curl_share.setopt(pycurl.SH_SHARE, pycurl.LOCK_DATA_DNS)

        if self.credentials:
            self.login(self.credentials)

    def _make_request(self, method: str, url: str, headers: Dict[str, str] = None, data: Any = None) -> PyCurlResponse:
        """Helper function to make HTTP requests using pycurl."""
        buffer = BytesIO()
        header_buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.SHARE, self.curl_share)
        curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        curl.setopt(pycurl.HEADERFUNCTION, header_buffer.write)
        curl.setopt(pycurl.FOLLOWLOCATION, True)

        if headers:
            curl.setopt(pycurl.HTTPHEADER, [f"{k}: {v}" for k, v in headers.items()])

        if method == 'POST':
            curl.setopt(pycurl.POST, True)
            if data:
                curl.setopt(pycurl.POSTFIELDS, data)
        elif method == 'PUT':
            curl.setopt(pycurl.CUSTOMREQUEST, 'PUT')
            if data:
                curl.setopt(pycurl.POSTFIELDS, data)
        elif method == 'GET':
            curl.setopt(pycurl.HTTPGET, True)

        try:
            curl.perform()
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
            headers = self._parse_headers(header_buffer.getvalue().decode('utf-8'))
            body = buffer.getvalue()
        finally:
            curl.close()

        return PyCurlResponse(body, status_code, headers)

    def _parse_headers(self, raw_headers: str) -> Dict[str, str]:
        """Parses raw headers into a dictionary."""
        headers = {}
        for line in raw_headers.splitlines():
            if ': ' in line:
                key, value = line.split(': ', 1)
                headers[key.lower()] = value
        return headers

    def login(self, credentials):
        """Login to Open Library with given credentials."""
        if 'username' in credentials._asdict():
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = urlencode(credentials._asdict())
        else:  # s3 login
            headers = {'Content-Type': 'application/json'}
            data = json.dumps(credentials._asdict())
        url = self.base_url + '/account/login'

        err = lambda e: logger.exception("Error at login: %s", e)

        @backoff.on_exception(on_giveup=err, **self.BACKOFF_KWARGS)
        def _login(url, headers, data):
            """Makes best effort to perform request w/ exponential backoff."""
            return self._make_request('POST', url, headers=headers, data=data)

        response = _login(url, headers, data)

        if 'set-cookie' not in response.headers:
            raise ValueError("No cookie set")

    def get_ol_response(self, path):
        """Makes best effort to perform request w/ exponential backoff."""
        url = self.base_url + path

        err = lambda e: logger.exception("Error retrieving OpenLibrary response: %s", e)

        @backoff.on_exception(on_giveup=err, **self.BACKOFF_KWARGS)
        def _get(url):
            return self._make_request('GET', url)

        response = _get(url)
        response.raise_for_status()
        return response

    def delete(self, olid, comment):
        """Delete a single Open Library entity by olid (str)."""
        data = json.dumps({'type': {'key': '/type/delete'}, '_comment': comment})
        url = self._generate_url_from_olid(olid)
        return self._make_request('PUT', url, headers={'Content-Type': 'application/json'}, data=data)

    def save_many(self, docs, comment):
        """Uses the Open Library save_many API endpoint."""
        headers = {
            'Opt': '"http://openlibrary.org/dev/docs/api"; ns=42',
            '42-comment': comment,
        }
        doc_json = [doc.json() for doc in docs]
        return self._make_request(
            'POST',
            f'{self.base_url}/api/save_many',
            headers=headers,
            data=json.dumps(doc_json),
        )

    def _generate_url_from_olid(self, olid):
        """Returns the .json url for an olid (str)."""
        ol_paths = {'OL..A': 'authors', 'OL..M': 'books', 'OL..W': 'works'}
        kind = re.sub(r'\d+', '..', olid)
        return f"{self.base_url}/{ol_paths[kind]}/{olid}.json"
