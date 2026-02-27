#!/usr/bin/env python

"""
Tests supported Hacker News API versions

@author john keck
@email robertjkeck
"""

import unittest
import json
import urllib3
from urllib3.exceptions import HTTPError


class HackerNews:
    def __init__(self):
        self.session = urllib3.PoolManager()

    def _get_sync(self, url):
        try:
            response = self.session.request('GET', url)
            if response.status != 200:
                raise HTTPError(f"HTTP error: {response.status}")
            return json.loads(response.data.decode('utf-8'))
        except HTTPError as e:
            raise HTTPError(f"Failed to fetch data: {e}")


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
        self.hn.session.clear()  # Properly close the PoolManager


if __name__ == '__main__':
    unittest.main()
