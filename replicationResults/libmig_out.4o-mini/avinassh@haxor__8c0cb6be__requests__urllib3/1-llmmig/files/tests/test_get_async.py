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


class TestGetAsync(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.url = 'https://hacker-news.firebaseio.com/v0/item/8863.json'
        self.err_url = 'https://hacker-news.firebaseio.com/v0/items/8863.json'
        self.http = urllib3.PoolManager()

    def test_get_async(self):
        response = self.http.request('GET', self.url)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['id'], 8863)
        self.assertEqual(data['by'], 'dhouston')

    def test_get_async_error(self):
        response = self.http.request('GET', self.err_url)
        self.assertEqual(response.status, 404)

    def tearDown(self):
        pass  # No session to close in urllib3

if __name__ == '__main__':
    unittest.main()
