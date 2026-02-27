"""Test cases for the OpenLibrary module"""

import json
import jsonpickle
import pytest
import requests
import unittest

from unittest.mock import Mock, call, patch, ANY
from cerberus import Validator  # Replaced jsonschema with cerberus

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
    r = requests.Response
    # Non 4xx status will trigger backoff retries
    r.status_code = 404
    kwargs = {'response': r}
    raise requests.HTTPError("test HTTPError", **kwargs)


class TestOpenLibrary(unittest.TestCase):
    @patch('olclient.openlibrary.OpenLibrary.login')
    def setUp(self, mock_login):
        self.ol = OpenLibrary()

    @patch('requests.Session.get')
    def test_get_olid_by_isbn(self, mock_get):
        isbn_key = 'ISBN:0374202915'
        isbn_bibkeys = {
            isbn_key: {
                'info_url': 'https://openlibrary.org/books/OL23575801M/Marie_LaVeau'
            }
        }
        mock_get.return_value.json.return_value = isbn_bibkeys
        olid = self.ol.Edition.get_olid_by_isbn('0374202915')
        mock_get.assert_called_with(
            f"{self.ol.base_url}/api/books.json?bibkeys={isbn_key}"
        )
        expected_olid = 'OL23575801M'
        self.assertTrue(
            olid == expected_olid, f"Expected olid {expected_olid}, got {olid}"
        )

    @patch('requests.Session.get')
    def test_get_olid_notfound_by_bibkey(self, mock_get):
        mock_get.json_data = {}
        edition = self.ol.Edition.get(isbn='foobar')
        assert edition is None

    @patch('requests.Session.get')
    def test_get_work_by_metadata(self, mock_get):
        doc = {
            "key": "/works/OL2514747W",
            "title": "The Autobiography of Benjamin Franklin",
        }
        search_results = {'start': 0, 'num_found': 1, 'docs': [doc]}
        title = "The Autobiography of Benjamin Franklin"
        mock_get.return_value.json.return_value = search_results
        book = self.ol.Work.search(title=title)
        mock_get.assert_called_with(f"{self.ol.base_url}/search.json?title={title}")
        canonical_title = book.canonical_title
        self.assertTrue(
            'franklin' in canonical_title,
            f"Expected 'franklin' to appear in result title: {canonical_title}",
        )

    @patch('requests.Session.get')
    def test_get_edition_by_isbn(self, mock_get):
        isbn_lookup_response = {
            'ISBN:0374202915': {
                'info_url': 'https://openlibrary.org/books/OL23575801M/Marie_LaVeau'
            }
        }
        edition_response = {'key': "/books/OL23575801M", 'title': 'test'}
        mock_get.return_value.json.side_effect = [
            isbn_lookup_response,
            edition_response,
        ]
        book = self.ol.Edition.get(isbn='0374202915')
        mock_get.assert_has_calls(
            [
                call(f"{self.ol.base_url}/api/books.json?bibkeys=ISBN:0374202915"),
                call().raise_for_status(),
                call().json(),
                call(f"{self.ol.base_url}/books/OL23575801M.json"),
                call().raise_for_status(),
                call().json(),
            ]
        )
        expected_olid = 'OL23575801M'
        self.assertTrue(
            book.olid == expected_olid,
            f"Expected olid {expected_olid}, got {book.olid}",
        )

    @patch('requests.Session.get')
    def test_matching_authors_olid(self, mock_get):
        author_autocomplete = [
            {'name': "Benjamin Franklin", 'key': "/authors/OL26170A"}
        ]
        mock_get.return_value.json.return_value = author_autocomplete
        name = 'Benjamin Franklin'
        got_olid = self.ol.Author.get_olid_by_name(name)
        expected_olid = 'OL26170A'
        self.assertTrue(
            got_olid == expected_olid, f"Expected olid {expected_olid}, got {got_olid}"
        )

    @patch('requests.Session.get')
    def test_create_book(self, mock_get):
        book = Book(
            publisher='Karamanolis',
            title='Alles ber Mikrofone',
            identifiers={'isbn_10': ['3922238246']},
            publish_date=1982,
            authors=[Author(name='Karl Schwarzer')],
            publish_location='Neubiberg bei Mnchen',
        )
        author_autocomplete = [{'name': "Karl Schwarzer", 'key': "/authors/OL7292805A"}]
        mock_get.return_value.json.return_value = author_autocomplete
        got_result = self.ol.create_book(book, debug=True)
        mock_get.assert_called_with(
            f"{self.ol.base_url}/authors/_autocomplete?q=Karl Schwarzer&limit=1"
        )
        expected_result = {
            '_save': '',
            'author_key': '/authors/OL7292805A',
            'author_name': 'Karl Schwarzer',
            'id_name': 'isbn_10',
            'id_value': '3922238246',
            'publish_date': 1982,
            'publisher': 'Karamanolis',
            'title': 'Alles ber Mikrofone',
        }
        self.assertTrue(
            got_result == expected_result,
            f"Expected create_book to return {expected_result}, got {got_result}",
        )

    def test_get_work(self):
        work_json = {'title': 'All Quiet on the Western Front'}
        work = self.ol.Work('OL12938932W', **work_json)
        self.assertTrue(
            work.title.lower() == 'all quiet on the western front',
            "Failed to retrieve work",
        )

    def test_work_json(self):
        authors = [
            {"type": "/type/author_role", "author": {"key": "/authors/OL5864762A"}}
        ]
        work = self.ol.Work('OL12938932W', key='/works/OL12938932W', authors=authors)
        work_json = work.json()
        self.assertEqual(work_json['key'], "/works/OL12938932W")
        self.assertEqual(
            work_json['authors'][0]['author']['key'], "/authors/OL5864762A"
        )

    def test_work_validation(self):
        work = self.ol.Work(
            'OL123W',
            title='Test Title',
            type={'key': '/type/work'},
            revision=1,
            last_modified={
                'type': '/type/datetime',
                'value': '2016-10-12T00:48:04.453554',
            },
        )
        self.assertIsNone(work.validate())

    def test_edition_json(self):
        author = self.ol.Author('OL123A', 'Test Author')
        edition = self.ol.Edition(
            edition_olid='OL123M',
            work_olid='OL123W',
            title='Test Title',
            authors=[author],
        )
        edition_json = edition.json()
        self.assertEqual(edition_json['key'], "/books/OL123M")
        self.assertEqual(edition_json['works'][0], {'key': '/works/OL123W'})
        self.assertEqual(edition_json['authors'][0], {'key': '/authors/OL123A'})

        self.assertNotIn('work_olid', edition_json)
        self.assertNotIn(
            'cover',
            edition_json,
            "'cover' is not a valid Edition property, should be list: 'covers'",
        )

    def test_edition_validation(self):
        author = self.ol.Author('OL123A', 'Test Author')
        edition = self.ol.Edition(
            edition_olid='OL123M',
            work_olid='OL123W',
            title='Test Title',
            type={'key': '/type/edition'},
            revision=1,
            last_modified={
                'type': '/type/datetime',
                'value': '2016-10-12T00:48:04.453554',
            },
            authors=[author],
        )
        self.assertIsNone(edition.validate())
        orphaned_edition = self.ol.Edition(
            edition_olid='OL123M', work_olid=None, title='Test Title', authors=[author]
        )
        validator = Validator({
            "edition_olid": {"type": "string", "required": True},
            "work_olid": {"type": "string", "nullable": True},
            "title": {"type": "string", "required": True},
        })
        self.assertFalse(validator.validate(orphaned_edition))
