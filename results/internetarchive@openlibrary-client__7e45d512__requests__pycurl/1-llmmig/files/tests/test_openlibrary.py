"""Test cases for the OpenLibrary module"""

import json
import jsonpickle
import jsonschema
import pytest
import pycurl
import unittest

from io import BytesIO
from unittest.mock import Mock, call, patch, ANY

from olclient.config import Config
from olclient.common import Author, Book
from olclient.openlibrary import OpenLibrary


def create_edition(ol, **kwargs):
    """Creates a basic test Edition."""
    defaults = {
        'edition_olid': 'OL123M',
        'work_olid': 'OL123W',
        'title': 'Test Title',
        'revision': 1,
        'last_modified': {
            'type': '/type/datetime',
            'value': '2016-10-12T00:48:04.453554',
        },
    }
    defaults.update(kwargs)
    return ol.Edition(**defaults)


def create_work(ol, **kwargs):
    """Creates a basic test Work."""
    defaults = {
        'olid': 'OL123W',
        'title': 'Test Title',
        'revision': 1,
        'last_modified': {
            'type': '/type/datetime',
            'value': '2016-10-12T00:48:04.453554',
        },
    }
    defaults.update(kwargs)
    return ol.Work(**defaults)


def raise_http_error():
    # Simulate an HTTP error with pycurl
    raise pycurl.error("HTTP Error: 404")


class TestOpenLibrary(unittest.TestCase):
    @patch('olclient.openlibrary.OpenLibrary.login')
    def setUp(self, mock_login):
        self.ol = OpenLibrary()

    @patch('pycurl.Curl')
    def test_get_olid_by_isbn(self, mock_curl):
        isbn_key = 'ISBN:0374202915'
        isbn_bibkeys = {
            isbn_key: {
                'info_url': 'https://openlibrary.org/books/OL23575801M/Marie_LaVeau'
            }
        }

        # Mock pycurl response
        buffer = BytesIO()
        buffer.write(json.dumps(isbn_bibkeys).encode('utf-8'))
        buffer.seek(0)
        mock_curl.return_value.perform.side_effect = lambda: buffer.seek(0)
        mock_curl.return_value.getinfo.return_value = 200

        olid = self.ol.Edition.get_olid_by_isbn('0374202915')
        mock_curl.return_value.setopt.assert_any_call(
            pycurl.URL, f"{self.ol.base_url}/api/books.json?bibkeys={isbn_key}"
        )
        expected_olid = 'OL23575801M'
        self.assertTrue(
            olid == expected_olid, f"Expected olid {expected_olid}, got {olid}"
        )

    @patch('pycurl.Curl')
    def test_get_olid_notfound_by_bibkey(self, mock_curl):
        # Mock pycurl response
        buffer = BytesIO()
        buffer.write(json.dumps({}).encode('utf-8'))
        buffer.seek(0)
        mock_curl.return_value.perform.side_effect = lambda: buffer.seek(0)
        mock_curl.return_value.getinfo.return_value = 404

        edition = self.ol.Edition.get(isbn='foobar')
        assert edition is None

    @patch('pycurl.Curl')
    def test_get_work_by_metadata(self, mock_curl):
        doc = {
            "key": "/works/OL2514747W",
            "title": "The Autobiography of Benjamin Franklin",
        }
        search_results = {'start': 0, 'num_found': 1, 'docs': [doc]}
        title = "The Autobiography of Benjamin Franklin"

        # Mock pycurl response
        buffer = BytesIO()
        buffer.write(json.dumps(search_results).encode('utf-8'))
        buffer.seek(0)
        mock_curl.return_value.perform.side_effect = lambda: buffer.seek(0)
        mock_curl.return_value.getinfo.return_value = 200

        book = self.ol.Work.search(title=title)
        mock_curl.return_value.setopt.assert_any_call(
            pycurl.URL, f"{self.ol.base_url}/search.json?title={title}"
        )
        canonical_title = book.canonical_title
        self.assertTrue(
            'franklin' in canonical_title,
            f"Expected 'franklin' to appear in result title: {canonical_title}",
        )

    @patch('pycurl.Curl')
    def test_get_edition_by_isbn(self, mock_curl):
        isbn_lookup_response = {
            'ISBN:0374202915': {
                'info_url': 'https://openlibrary.org/books/OL23575801M/Marie_LaVeau'
            }
        }
        edition_response = {'key': "/books/OL23575801M", 'title': 'test'}

        # Mock pycurl response
        buffer1 = BytesIO()
        buffer1.write(json.dumps(isbn_lookup_response).encode('utf-8'))
        buffer1.seek(0)

        buffer2 = BytesIO()
        buffer2.write(json.dumps(edition_response).encode('utf-8'))
        buffer2.seek(0)

        mock_curl.return_value.perform.side_effect = [lambda: buffer1.seek(0), lambda: buffer2.seek(0)]
        mock_curl.return_value.getinfo.return_value = 200

        book = self.ol.Edition.get(isbn='0374202915')
        mock_curl.return_value.setopt.assert_any_call(
            pycurl.URL, f"{self.ol.base_url}/api/books.json?bibkeys=ISBN:0374202915"
        )
        expected_olid = 'OL23575801M'
        self.assertTrue(
            book.olid == expected_olid,
            f"Expected olid {expected_olid}, got {book.olid}",
        )

    # Additional tests would follow the same pattern, replacing `requests` with `pycurl`.

