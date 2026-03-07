#!/usr/bin/env python

"""
Tests supported Hacker News API versions

@author john keck
@email robertjkeck2@gmail.com
"""

import unittest
import urllib3
import json

from hackernews import HackerNews
from hackernews import HTTPError


class TestGetSync(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.url = 'https://hacker-news.firebaseio.com/v0/item/8863.json'
        self.err_url = 'https://hacker-news.firebaseio.com/v0/items/8863.json'
        self.http = urllib3.PoolManager()

    def test_get_sync(self):
        response = self.http.request('GET', self.url)
        if response.status != 200:
            raise HTTPError(f"HTTP Error: {response.status}")
        data = json.loads(response.data)
        self.assertEqual(data['id'], 8863)
        self.assertEqual(data['by'], 'dhouston')

    def test_get_sync_error(self):
        response = self.http.request('GET', self.err_url)
        if response.status != 200:
            raise HTTPError(f"HTTP Error: {response.status}")

    def tearDown(self):
        pass  # No session to close in urllib3

if __name__ == '__main__':
    unittest.main()
