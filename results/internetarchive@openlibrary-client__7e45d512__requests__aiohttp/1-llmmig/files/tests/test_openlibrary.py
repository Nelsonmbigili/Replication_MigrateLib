"""Test cases for the OpenLibrary module"""

import json
import jsonpickle
import jsonschema
import pytest
import aiohttp
import unittest
import asyncio

from unittest.mock import AsyncMock, call, patch, ANY

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


async def raise_http_error():
    response = AsyncMock()
    response.status = 404
    response.raise_for_status.side_effect = aiohttp.ClientResponseError(
        status=404, message="test HTTPError"
    )
    raise response.raise_for_status()


class TestOpenLibrary(unittest.TestCase):
    @patch('olclient.openlibrary.OpenLibrary.login')
    def setUp(self, mock_login):
        self.ol = OpenLibrary()

    @patch('aiohttp.ClientSession.get', new_callable=AsyncMock)
    def test_get_olid_by_isbn(self, mock_get):
        async def run_test():
            isbn_key = 'ISBN:0374202915'
            isbn_bibkeys = {
                isbn_key: {
                    'info_url': 'https://openlibrary.org/books/OL23575801M/Marie_LaVeau'
                }
            }
            mock_get.return_value.__aenter__.return_value.json = AsyncMock(
                return_value=isbn_bibkeys
            )
            olid = await self.ol.Edition.get_olid_by_isbn('0374202915')
            mock_get.assert_called_with(
                f"{self.ol.base_url}/api/books.json?bibkeys={isbn_key}"
            )
            expected_olid = 'OL23575801M'
            self.assertTrue(
                olid == expected_olid, f"Expected olid {expected_olid}, got {olid}"
            )

        asyncio.run(run_test())

    @patch('aiohttp.ClientSession.get', new_callable=AsyncMock)
    def test_get_olid_notfound_by_bibkey(self, mock_get):
        async def run_test():
            mock_get.return_value.__aenter__.return_value.json = AsyncMock(
                return_value={}
            )
            edition = await self.ol.Edition.get(isbn='foobar')
            assert edition is None

        asyncio.run(run_test())

    @patch('aiohttp.ClientSession.get', new_callable=AsyncMock)
    def test_get_work_by_metadata(self, mock_get):
        async def run_test():
            doc = {
                "key": "/works/OL2514747W",
                "title": "The Autobiography of Benjamin Franklin",
            }
            search_results = {'start': 0, 'num_found': 1, 'docs': [doc]}
            title = "The Autobiography of Benjamin Franklin"
            mock_get.return_value.__aenter__.return_value.json = AsyncMock(
                return_value=search_results
            )
            book = await self.ol.Work.search(title=title)
            mock_get.assert_called_with(f"{self.ol.base_url}/search.json?title={title}")
            canonical_title = book.canonical_title
            self.assertTrue(
                'franklin' in canonical_title,
                f"Expected 'franklin' to appear in result title: {canonical_title}",
            )

        asyncio.run(run_test())

    @patch('aiohttp.ClientSession.get', new_callable=AsyncMock)
    def test_get_edition_by_isbn(self, mock_get):
        async def run_test():
            isbn_lookup_response = {
                'ISBN:0374202915': {
                    'info_url': 'https://openlibrary.org/books/OL23575801M/Marie_LaVeau'
                }
            }
            edition_response = {'key': "/books/OL23575801M", 'title': 'test'}
            mock_get.return_value.__aenter__.return_value.json.side_effect = [
                isbn_lookup_response,
                edition_response,
            ]
            book = await self.ol.Edition.get(isbn='0374202915')
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

        asyncio.run(run_test())

    @patch('aiohttp.ClientSession.get', new_callable=AsyncMock)
    def test_matching_authors_olid(self, mock_get):
        async def run_test():
            author_autocomplete = [
                {'name': "Benjamin Franklin", 'key': "/authors/OL26170A"}
            ]
            mock_get.return_value.__aenter__.return_value.json = AsyncMock(
                return_value=author_autocomplete
            )
            name = 'Benjamin Franklin'
            got_olid = await self.ol.Author.get_olid_by_name(name)
            expected_olid = 'OL26170A'
            self.assertTrue(
                got_olid == expected_olid, f"Expected olid {expected_olid}, got {got_olid}"
            )

        asyncio.run(run_test())

    @patch('aiohttp.ClientSession.post', new_callable=AsyncMock)
    def test_save_many(self, mock_post):
        async def run_test():
            edition = self.ol.Edition(
                edition_olid='OL123M', work_olid='OL12W', title='minimal edition'
            )
            work = self.ol.Work(olid='OL12W', title='minimal work')
            await self.ol.save_many([edition, work], "test comment")
            mock_post.assert_called_with(
                f"{self.ol.base_url}/api/save_many", ANY, headers=ANY
            )
            called_with_json = json.loads(mock_post.call_args[0][1])
            called_with_headers = mock_post.call_args[1]['headers']
            assert len(called_with_json) == 2
            self.assertIn('ns=42', called_with_headers['Opt'])
            self.assertEqual('test comment', called_with_headers['42-comment'])

        asyncio.run(run_test())
