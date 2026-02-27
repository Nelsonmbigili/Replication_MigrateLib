#!/usr/bin/env python

"""
Tests supported Hacker News API versions

@author john keck
@email robertjkeck
"""

import unittest
from requests_futures.sessions import FuturesSession  # Updated import
from hackernews import HackerNews
from hackernews import HTTPError


class HackerNews:
    def __init__(self):
        self.session = FuturesSession()  # Use FuturesSession instead of requests.Session

    def _get_sync(self, url):
        # Make the request asynchronously but wait for the result to keep it synchronous
        future = self.session.get(url)
        response = future.result()  # Wait for the response
        if response.status_code != 200:
            raise HTTPError(f"HTTP error: {response.status_code}")
        return response.json()


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
        self.hn.session.close()  # Close the FuturesSession

if __name__ == '__main__':
    unittest.main()
