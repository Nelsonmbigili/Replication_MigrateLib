"""Basic wrapper (client) over OpenLibrary REST API"""

import json
from typing import List, Dict, Optional, Any

import jsonschema
import logging
import os
import re
from urllib.parse import urlencode
from urllib.request import pathname2url

import backoff
from requests_futures.sessions import FuturesSession
from requests_futures.sessions import Response

from olclient import common
from olclient.config import Config
from olclient.entity_helpers.work import get_work_helper_class
from olclient.utils import merge_unique_lists

logger = logging.getLogger('openlibrary')


class OpenLibrary:

    """Open Library API Client."""

    VALID_IDS = ['isbn_10', 'isbn_13', 'lccn', 'ocaid']
    BACKOFF_KWARGS = {
        'wait_gen': backoff.expo,
        'exception': Exception,  # Updated to handle FuturesSession exceptions
        'giveup': lambda e: hasattr(e.response, 'status_code')
        and 400 <= e.response.status_code < 500,
        'max_tries': 5,
    }

    # constants to aid works.json API request's pagination
    WORKS_LIMIT = 50
    WORKS_PAGINATION_OFFSET = 0

    def __init__(self, credentials=None, base_url='https://openlibrary.org'):
        self.session = FuturesSession()  # Use FuturesSession for async requests
        self.base_url = base_url
        credentials = credentials or Config().get_config().get('s3', None)
        if credentials:
            self.login(credentials)

    def login(self, credentials):
        """Login to Open Library with given credentials, ensures the requests
        session has valid cookies for future requests.
        """

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
            """Makes best effort to perform request w/ exponential backoff"""
            future = self.session.post(url, data=data, headers=headers)
            return future.result()  # Block until the response is available

        _ = _login(url, headers, data)

        if not self.session.cookies:
            raise ValueError("No cookie set")

    def get_ol_response(self, path):
        """Makes best effort to perform request w/ exponential backoff"""
        err = lambda e: logger.exception("Error retrieving OpenLibrary response: %s", e)

        @backoff.on_exception(on_giveup=err, **self.BACKOFF_KWARGS)
        def _get_response():
            future = self.session.get(self.base_url + path)
            response = future.result()  # Block until the response is available
            response.raise_for_status()
            return response

        return _get_response()

    def save_many(self, docs, comment) -> Response:
        """
        Uses the Open Library save_many API endpoint to
        write any number or combination of documents (Edition, Work, or Author)
        back to Open Library.
        Uses HTTP Extension Framework custom headers (RFC 2774).
        """
        headers = {
            'Opt': '"http://openlibrary.org/dev/docs/api"; ns=42',
            '42-comment': comment,
        }
        doc_json = [doc.json() for doc in docs]
        future = self.session.post(
            f'{self.base_url}/api/save_many', json.dumps(doc_json), headers=headers
        )
        return future.result()  # Block until the response is available

    def delete(self, olid, comment):
        """Delete a single Open Library entity by olid (str)"""
        data = json.dumps({'type': {'key': '/type/delete'}, '_comment': comment})
        url = self._generate_url_from_olid(olid)
        future = self.session.put(url, data=data)
        return future.result()  # Block until the response is available

    def _create_book_post(self, url, data):
        """Makes best effort to perform request w/ exponential backoff"""
        err = lambda e: logger.exception("Error creating OpenLibrary book: %s", e)

        @backoff.on_exception(on_giveup=err, **self.BACKOFF_KWARGS)
        def _post():
            future = self.session.post(url, data=data)
            return future.result()  # Block until the response is available

        return _post()

    def _generate_url_from_olid(self, olid):
        """Returns the .json url for an olid (str)"""
        ol_paths = {'OL..A': 'authors', 'OL..M': 'books', 'OL..W': 'works'}
        kind = re.sub(r'\d+', '..', olid)
        return f"{self.base_url}/{ol_paths[kind]}/{olid}.json"

    # Other methods remain unchanged
