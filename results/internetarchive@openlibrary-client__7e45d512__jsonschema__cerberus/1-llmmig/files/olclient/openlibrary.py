"""Basic wrapper (client) over OpenLibrary REST API"""

import json
from typing import List, Dict, Optional, Any

import cerberus  # Replaced jsonschema with cerberus
import logging
import os
import re
from urllib.parse import urlencode
from urllib.request import pathname2url

import backoff
import requests
from requests import Response

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
        'exception': requests.exceptions.RequestException,
        'giveup': lambda e: hasattr(e.response, 'status_code')
        and 400 <= e.response.status_code < 500,
        'max_tries': 5,
    }

    WORKS_LIMIT = 50
    WORKS_PAGINATION_OFFSET = 0

    def __init__(self, credentials=None, base_url='https://openlibrary.org'):
        self.session = requests.Session()
        self.base_url = base_url
        credentials = credentials or Config().get_config().get('s3', None)
        if credentials:
            self.login(credentials)

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
            """Makes best effort to perform request w/ exponential backoff"""
            return self.session.post(url, data=data, headers=headers)

        _ = _login(url, headers, data)

        if not self.session.cookies:
            raise ValueError("No cookie set")

    def validate(self, doc, schema_name):
        """Validates a doc's JSON representation against its schema using cerberus.

        Args:
            doc: The document to validate.
            schema_name: The name of the schema file.

        Returns:
            None

        Raises:
            ValueError: If validation fails.
        """
        path = os.path.dirname(os.path.realpath(__file__))
        schemata_path = os.path.join(path, 'schemata', schema_name)
        with open(schemata_path) as schema_data:
            schema = json.load(schema_data)
            validator = cerberus.Validator(schema)  # Initialize cerberus Validator
            if not validator.validate(doc.json()):  # Validate the document
                raise ValueError(f"Validation failed: {validator.errors}")

    def delete(self, olid, comment):
        """Delete a single Open Library entity by olid (str)."""
        data = json.dumps({'type': {'key': '/type/delete'}, '_comment': comment})
        url = self._generate_url_from_olid(olid)
        return self.session.put(url, data=data)

    def save_many(self, docs, comment) -> Response:
        """Uses the Open Library save_many API endpoint."""
        headers = {
            'Opt': '"http://openlibrary.org/dev/docs/api"; ns=42',
            '42-comment': comment,
        }
        doc_json = [doc.json() for doc in docs]
        return self.session.post(
            f'{self.base_url}/api/save_many', json.dumps(doc_json), headers=headers
        )

    def delete_many(self, ol_ids: List[str], comment: str) -> Response:
        return self.save_many(
            [self.Delete(ol_id) for ol_id in ol_ids],
            comment=comment
        )

    err = lambda e: logger.exception("Error retrieving OpenLibrary response: %s", e)

    @backoff.on_exception(on_giveup=err, **BACKOFF_KWARGS)  # type: ignore
    def get_ol_response(self, path):
        """Makes best effort to perform request w/ exponential backoff"""
        response = self.session.get(self.base_url + path)
        response.raise_for_status()
        return response

    @property
    def Work(self):
        return get_work_helper_class(self)

    @property
    def Edition(ol_self):
        class Edition(common.Book):
            OL = ol_self

            def validate(self):
                """Validates an Edition's JSON representation."""
                return self.OL.validate(self, 'edition.schema.json')

        return Edition

    @property
    def Author(ol_self):
        class Author(common.Author):
            OL = ol_self

            def validate(self):
                """Validates an Author's JSON representation."""
                return self.OL.validate(self, 'author.schema.json')

        return Author

    @property
    def Delete(ol_self):
        class Delete(common.Entity):
            OL = ol_self

            def json(self):
                data = {
                    'key': OpenLibrary.full_key(self.olid),
                    'type': {'key': '/type/delete'},
                }
                return data

        return Delete

    @staticmethod
    def full_key(olid):
        """Returns the Open Library JSON key."""
        return f"/{OpenLibrary.get_type(olid)}s/{olid}"

    @staticmethod
    def get_type(olid):
        ol_types = {'OL..A': 'author', 'OL..M': 'book', 'OL..W': 'work'}
        kind = re.sub(r'\d+', '..', olid)
        try:
            return ol_types[kind]
        except KeyError:
            raise ValueError(f"Unknown type for olid: {olid}")
