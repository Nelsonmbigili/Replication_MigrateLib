#!/usr/bin/env python

"""
Tests supported Hacker News API versions

@author john keck
@email robertjke
"""

import unittest
import httpx  # Migrated to httpx

from hackernews import HackerNews
from hackernews import HTTPError


class HackerNews:
    def __init__(self):
        self.session = httpx.Client()  # Use httpx.Client instead of requests.Session

    def _get_sync(self, url):
        try:
            response = self.session.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except httpx.HTTPStatusError as e:  # Use httpx.HTTPStatusError
            raise HTTPError(f"HTTP error occurred: {e}") from e
        except httpx.RequestError as e:  # Handle other request-related errors
            raise HTTPError(f"Request error occurred: {e}") from e


class TestGetSync(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.url = 'https://hacker-news.firebaseio.com/v0/item/8863.json'
        self.err_url = 'https://hacker-news.firebaseio.com/v0/items/8863.json'

    def test_get_sync(self):
        response = self.hn._get_sync(self.url)
        self.assertEqual(response['id'], 8863)
        self.assertEqual(response['by'], 'dhouston')

    def test_get_sync_error(self):
        self.assertRaises(HTTPError, self.hn._get_sync, self.err_url)

    def tearDown(self):
        self.hn.session.close()  # Close the httpx.Client session

if __name__ == '__main__':
    unittest.main()
